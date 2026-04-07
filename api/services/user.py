from __future__ import annotations

from pydantic import create_model
from sqlalchemy.ext.asyncio import AsyncSession

from core.dao import UserDAO
from core.errors import NotFoundError, EmailAlreadyVerifiedError
from core.models import User


async def get_user_by_id(session: AsyncSession, user_id: int) -> User:
    user = await UserDAO.get_one_by_id(session, user_id)
    if user is None:
        raise NotFoundError
    return user


async def verify_email(session: AsyncSession, user_id: int):
    user = await get_user_by_id(session, user_id)
    if user.verified_email:
        raise EmailAlreadyVerifiedError
    VerifiedEmail = create_model("VerifiedEmail", verified_email=(bool, ...))
    await UserDAO.update(session, user, VerifiedEmail(verified_email=True))
    await session.commit()
