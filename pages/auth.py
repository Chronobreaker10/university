from typing import Annotated

from fastapi import APIRouter, Request, Depends
from fastapi import status, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.user import get_current_user
from api.services.user import authenticate_user
from core.config import settings
from core.database import db_helper
from core.schemas import UserAuth, UserRead

router = APIRouter(prefix="/auth", tags=["Авторизация"])
templates = Jinja2Templates(directory="templates")


@router.get("/profile", name="auth.profile")
async def get_profile(request: Request, current_user: Annotated[UserRead, Depends(get_current_user)]):
    # token = request.cookies.get(settings.security.cookie_name)
    message = request.session.pop("flashed_message", "")
    return templates.TemplateResponse("auth/profile.html",
                                      {"request": request, "title": "Мой профиль", "message": message,
                                       "current_user": current_user})


@router.get("/login", name="auth.login_form")
async def login_form(request: Request):
    token = request.cookies.get(settings.security.cookie_name)
    if not token:
        message = request.session.pop("flashed_message", "")
        return templates.TemplateResponse("auth/login.html",
                                          {"request": request, "title": "Авторизация", "message": message})
    else:
        request.session["flashed_message"] = {
            "type": "success",
            "text": "Вы уже вошли в систему!"
        }
        return RedirectResponse(url=request.url_for("students.index"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/login", name="auth.login")
async def login(request: Request, credentials: Annotated[UserAuth, Form()],
                session: Annotated[AsyncSession, Depends(db_helper.get_session())]):
    token = request.cookies.get(settings.security.cookie_name)
    if not token:
        token = await authenticate_user(session, credentials.email, credentials.password)
        response = RedirectResponse(url=request.url_for("students.index"), status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(settings.security.cookie_name, token, httponly=True,
                            expires=settings.security.expires_minutes * 60)
        request.session["flashed_message"] = {
            "type": "success",
            "text": "Вход успешно выполнен!"
        }
        return response
    else:
        request.session["flashed_message"] = {
            "type": "success",
            "text": "Вы уже вошли в систему!"
        }
        return RedirectResponse(url=request.url_for("students.index"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/logout", name="auth.logout")
async def logout(request: Request):
    response = RedirectResponse(url=request.url_for("auth.login_form"), status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(settings.security.cookie_name)
    request.session["flashed_message"] = {
        "type": "success",
        "text": "Вы успешно вышли из системы!"
    }
    return response
