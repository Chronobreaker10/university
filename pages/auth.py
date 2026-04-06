from __future__ import annotations

from typing import Annotated
from functools import wraps
from fastapi import APIRouter, Request, Depends, Query
from fastapi import status, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_csrf_protect import CsrfProtect
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.user import get_current_user
from api.services.auth import login_user, register_user, logout_user
from core.config import settings
from core.database import db_helper
from fastapi.encoders import jsonable_encoder

from core.errors import UnauthorizedError
from core.models import User
from core.schemas import UserAuth, UserRead, UserCreate, UserRegister, FlashMessage, MessageStatus

router = APIRouter(prefix="/auth", tags=["Авторизация"])
templates = Jinja2Templates(directory="templates")


def check_cookie(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        token = request.cookies.get(settings.security.access_token_cookie_name)
        if not token:
            return await func(request, *args, **kwargs)
        else:
            request.session["flashed_message"] = jsonable_encoder(FlashMessage(status=MessageStatus.SUCCESS,
                                                                               text="Вы уже вошли в систему!"))
            return RedirectResponse(url=request.url_for("students.index"), status_code=status.HTTP_303_SEE_OTHER)

    return wrapper


@router.get("/profile", name="auth.profile")
async def get_profile(request: Request, current_user: Annotated[UserRead, Depends(get_current_user)]):
    # token = request.cookies.get(settings.security.cookie_name)
    message = request.session.pop("flashed_message", "")
    return templates.TemplateResponse("auth/profile.html",
                                      {"request": request, "title": "Мой профиль",
                                       "current_user": current_user, "message": message})


@router.get("/login", name="auth.login_form")
@check_cookie
async def login_form(request: Request, csrf_protect: Annotated[CsrfProtect, Depends()]):
    message = request.session.pop("flashed_message", "")
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse("auth/login.html",
                                          {"request": request, "title": "Авторизация", "message": message,
                                           "csrf_token": csrf_token})
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@router.get("/register", name="auth.register_form")
@check_cookie
async def register_form(request: Request):
    message = request.session.pop("flashed_message", "")
    return templates.TemplateResponse("auth/register.html",
                                      {"request": request, "title": "Регистрация", "message": message})


@router.post("/login", name="auth.login")
@check_cookie
async def login(request: Request, credentials: Annotated[UserAuth, Form()],
                session: Annotated[AsyncSession, Depends(db_helper.get_session())],
                csrf_protect: Annotated[CsrfProtect, Depends()],
                next_redirect: Annotated[str | None, Query(alias="next")] = None):
    await csrf_protect.validate_csrf(request)
    access_token, refresh_token, user = await login_user(session, credentials.email, credentials.password)
    url = request.url_for("students.index")
    if next_redirect:
        url = next_redirect
    response = RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(settings.security.access_token_cookie_name, access_token, httponly=True,
                        expires=settings.security.access_token_expires_minutes * 60)
    response.set_cookie(settings.security.refresh_token_cookie_name, refresh_token, httponly=True,
                        expires=settings.security.refresh_token_expires_days * 24 * 60 * 60)
    request.session["flashed_message"] = jsonable_encoder(FlashMessage(status=MessageStatus.SUCCESS,
                                                                       text="Вход успешно выполнен!"))
    request.session["current_user"] = jsonable_encoder(user)
    csrf_protect.unset_csrf_cookie(response)
    return response


@router.post("/register", name="auth.register")
@check_cookie
async def register(request: Request, data: Annotated[UserRegister, Form()],
                   session: Annotated[AsyncSession, Depends(db_helper.get_session())]):
    user_data = UserCreate.model_validate(data.model_dump(exclude={"repeat_password"}))
    await register_user(session, user_data)
    access_token, refresh_token = await login_user(session, data.email, data.hashed_password)
    response = RedirectResponse(url=request.url_for("students.index"), status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(settings.security.access_token_cookie_name, access_token, httponly=True,
                        expires=settings.security.access_token_expires_minutes * 60)
    response.set_cookie(settings.security.refresh_token_cookie_name, refresh_token, httponly=True,
                        expires=settings.security.refresh_token_expires_days * 24 * 60 * 60)
    request.session["flashed_message"] = FlashMessage(status=MessageStatus.SUCCESS,
                                                      text="Вход успешно выполнен!").model_dump()
    return response


@router.post("/logout", name="auth.logout")
async def logout(request: Request, current_user: Annotated[User, Depends(get_current_user)]):
    refresh_token = request.cookies.get(settings.security.refresh_token_cookie_name)
    if not refresh_token:
        raise UnauthorizedError
    await logout_user(current_user, refresh_token)
    response = RedirectResponse(url=request.url_for("auth.login_form"), status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(settings.security.access_token_cookie_name)
    response.delete_cookie(settings.security.refresh_token_cookie_name)
    request.session["flashed_message"] = FlashMessage(status=MessageStatus.SUCCESS,
                                                      text="Вы успешно вышли из системы!").model_dump()
    return response
