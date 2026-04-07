from __future__ import annotations

from fastapi import status


class BaseError(Exception):
    code: int
    message: str
    redirect_to: str | None = None
    flash: bool = False


class DatabaseError(BaseError):
    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "При работе с базой данных произошла ошибка"


class NotFoundError(BaseError):
    code = status.HTTP_404_NOT_FOUND
    message = "Запрашиваемый ресурс не найден"


class UserAlreadyExistsError(BaseError):
    code = status.HTTP_409_CONFLICT
    message = "Пользователь уже существует"
    flash = True


class StudentAlreadyExistsError(BaseError):
    code = status.HTTP_409_CONFLICT
    message = "Студент уже существует"
    redirect_to = "students.create"
    flash = True


class UnauthorizedError(BaseError):
    code = status.HTTP_401_UNAUTHORIZED
    message = "Для доступа к ресурсу необходимо авторизоваться"
    redirect_to = "auth.login_form"

    def __init__(self, message: str = None):
        self.message = message or self.message


class EmailAlreadyVerifiedError(BaseError):
    code = status.HTTP_409_CONFLICT
    message = "Email уже подтвержден!"
    redirect_to = "auth.profile"



class InvalidCredentialsError(BaseError):
    code = status.HTTP_401_UNAUTHORIZED
    message = "Проверьте логин и пароль"
    redirect_to = "auth.login_form"


class ForbiddenError(BaseError):
    code = status.HTTP_403_FORBIDDEN
    message = "Доступ запрещен"
