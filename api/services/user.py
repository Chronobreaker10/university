from __future__ import annotations

from pydantic import create_model
from sqlalchemy.ext.asyncio import AsyncSession

from core.dao import UserDAO
from core.errors import NotFoundError, UnauthorizedError
from core.models import User
from core.schemas import UserCreate
from core.security.auth import get_password_hash, verify_password, create_access_token


async def register_user(session: AsyncSession, data: UserCreate) -> int:
    new_user = data.model_copy(update={"hashed_password": get_password_hash(data.hashed_password)})
    result = await UserDAO.create(session, new_user)
    return result


async def get_user_by_id(session: AsyncSession, user_id: int) -> User:
    user = await UserDAO.get_one_by_id(session, user_id)
    if user is None:
        raise NotFoundError
    return user


async def authenticate_user(session: AsyncSession, email: str, password: str) -> str:
    UserEmail = create_model("UserEmail", email=(str, ...))
    user = await UserDAO.find_one_or_none(session, UserEmail(email=email))
    if not user or not verify_password(password, user.hashed_password):
        raise UnauthorizedError
    token = create_access_token(data={"sub": str(user.id)})
    return token
