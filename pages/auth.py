from typing import Annotated
from functools import wraps
from fastapi import APIRouter, Request, Depends
from fastapi import status, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.user import get_current_user
from api.services.user import authenticate_user, register_user
from core.config import settings
from core.database import db_helper
from core.schemas import UserAuth, UserRead, UserCreate, UserRegister

router = APIRouter(prefix="/auth", tags=["Авторизация"])
templates = Jinja2Templates(directory="templates")


def check_cookie(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        token = request.cookies.get(settings.security.cookie_name)
        if not token:
            return await func(request, *args, **kwargs)
        else:
            request.session["flashed_message"] = {
                "type": "success",
                "text": "Вы уже вошли в систему!"
            }
            return RedirectResponse(url=request.url_for("students.index"), status_code=status.HTTP_303_SEE_OTHER)
    return wrapper


@router.get("/profile", name="auth.profile")
async def get_profile(request: Request, current_user: Annotated[UserRead, Depends(get_current_user)]):
    # token = request.cookies.get(settings.security.cookie_name)
    message = request.session.pop("flashed_message", "")
    return templates.TemplateResponse("auth/profile.html",
                                      {"request": request, "title": "Мой профиль", "message": message,
                                       "current_user": current_user})


@router.get("/login", name="auth.login_form")
@check_cookie
async def login_form(request: Request):
    message = request.session.pop("flashed_message", "")
    return templates.TemplateResponse("auth/login.html",
                                      {"request": request, "title": "Авторизация", "message": message})


@router.get("/register", name="auth.register_form")
@check_cookie
async def register_form(request: Request):
    message = request.session.pop("flashed_message", "")
    return templates.TemplateResponse("auth/register.html",
                                      {"request": request, "title": "Регистрация", "message": message})


@router.post("/login", name="auth.login")
@check_cookie
async def login(request: Request, credentials: Annotated[UserAuth, Form()],
                session: Annotated[AsyncSession, Depends(db_helper.get_session())]):
    token = await authenticate_user(session, credentials.email, credentials.password)
    response = RedirectResponse(url=request.url_for("students.index"), status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(settings.security.cookie_name, token, httponly=True,
                        expires=settings.security.expires_minutes * 60)
    request.session["flashed_message"] = {
        "type": "success",
        "text": "Вход успешно выполнен!"
    }
    return response

@router.post("/register", name="auth.register")
@check_cookie
async def register(request: Request, data: Annotated[UserRegister, Form()],
                session: Annotated[AsyncSession, Depends(db_helper.get_session())]):
    user_data = UserCreate.model_validate(data.model_dump(exclude={"repeat_password"}))
    await register_user(session, user_data)
    token = await authenticate_user(session, data.email, data.hashed_password)
    response = RedirectResponse(url=request.url_for("students.index"), status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(settings.security.cookie_name, token, httponly=True,
                        expires=settings.security.expires_minutes * 60)
    request.session["flashed_message"] = {
        "type": "success",
        "text": "Вход успешно выполнен!"
    }
    return response

@router.post("/logout", name="auth.logout")
async def logout(request: Request):
    response = RedirectResponse(url=request.url_for("auth.login_form"), status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(settings.security.cookie_name)
    request.session["flashed_message"] = {
        "type": "success",
        "text": "Вы успешно вышли из системы!"
    }
    return response
