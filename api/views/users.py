from typing import Annotated

from fastapi import APIRouter, Depends, status, Path
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

import api.services.user as service
import api.services.auth as auth_service
from api.dependencies.user import get_current_user
from core.config import settings
from core.models import User
from core.schemas import UserCreate, UserRead, UserAuth, Token, DefaultResponse
from core.database import db_helper

router = APIRouter(prefix='/users', tags=['Пользователи'])


# @router.get("/", summary="Получить список всех студентов", response_model=list[StudentRead])
# async def get_all_students(session: Annotated[AsyncSession, Depends(get_session())],
#                            student_filter: Annotated[StudentFilter, Query()]):
#     return await service.get_students_by_filter(session, student_filter)


@router.get("/me", summary="Получить информацию о текущем пользователе", response_model=UserRead)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.get("/{user_id}", summary="Получить пользователя по ID", response_model=UserRead)
async def get_user_by_id(session: Annotated[AsyncSession, Depends(db_helper.get_session())],
                         user_id: Annotated[int, Path(ge=1, le=1000, title="ID", description="ID")]):
    return await service.get_user_by_id(session, user_id)


@router.post("/register", summary="Зарегистрироваться", response_model=DefaultResponse,
             status_code=status.HTTP_201_CREATED)
async def register(session: Annotated[AsyncSession, Depends(db_helper.get_session())], user: UserCreate):
    user_id = await auth_service.register_user(session, user)
    return {
        "message": f"Пользователь {user_id} успешно зарегистрирован"
    }


@router.post("/login", summary="Войти", response_model=Token)
async def login(session: Annotated[AsyncSession, Depends(db_helper.get_session())], response: Response,
                credentials: UserAuth):
    access_token, refresh_token = await auth_service.login_user(session, credentials.email, credentials.password)
    response.set_cookie(settings.security.access_token_cookie_name, access_token, httponly=True,
                        expires=settings.security.access_token_expires_minutes * 60)
    response.set_cookie(settings.security.refresh_token_cookie_name, refresh_token, httponly=True,
                       expires=settings.security.refresh_token_expires_days * 24 * 60 * 60)
    return Token(token=access_token)


@router.post("/logout", summary="Выйти", response_model=DefaultResponse)
async def logout(response: Response):
    response.delete_cookie(settings.security.cookie_name)
    return {"message": "Вы успешно вышли из системы"}
