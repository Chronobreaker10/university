from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from core.dao import UserDAO
from core.errors import NotFoundError
from core.models import User


async def get_user_by_id(session: AsyncSession, user_id: int) -> User:
    user = await UserDAO.get_one_by_id(session, user_id)
    if user is None:
        raise NotFoundError
    return user
