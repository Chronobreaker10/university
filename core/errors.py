from __future__ import annotations

from fastapi import status


class BaseError(Exception):
    code: int
    message: str


class RedirectError(Exception):
    code: int
    message: str
    redirect_to: str | None = None


class DatabaseError(RedirectError):
    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "При работе с базой данных произошла ошибка"


class NotFoundError(BaseError):
    code = status.HTTP_404_NOT_FOUND
    message = "Запрашиваемый ресурс не найден"


class UserAlreadyExistsError(BaseError):
    code = status.HTTP_409_CONFLICT
    message = "Пользователь уже существует"


class StudentAlreadyExistsError(RedirectError):
    code = status.HTTP_409_CONFLICT
    message = "Студент уже существует"


class UnauthorizedError(RedirectError):
    code = status.HTTP_401_UNAUTHORIZED
    message = "Неверный email или пароль"
    redirect_to = "auth.login_form"

    def __init__(self, message: str = None):
        self.message = message or self.message


class ForbiddenError(RedirectError):
    code = status.HTTP_403_FORBIDDEN
    message = "Доступ запрещен"
