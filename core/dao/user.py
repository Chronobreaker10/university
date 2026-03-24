from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.dao.base import BaseDAO
from core.models import User
from core.errors import UserAlreadyExistsError
from sqlalchemy.exc import IntegrityError


class UserDAO(BaseDAO[User]):
    Model = User

    @classmethod
    async def create(cls, session: AsyncSession, data: BaseModel) -> Model:
        try:
            return await super().create(session, data)
        except IntegrityError as e:
            raise UserAlreadyExistsError from e
