from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request, Depends
from core.config import settings
from core.models import User
from core.security.auth import validate_token
from core.errors import UnauthorizedError, ForbiddenError
import api.services.user as service
from core.database import db_helper
from core.models import Role


async def get_current_user(session: Annotated[AsyncSession, Depends(db_helper.get_session())],
                           request: Request) -> User:
    token = request.cookies.get(settings.security.cookie_name)
    if not token:
        raise UnauthorizedError("Для доступа к ресурсу необходимо авторизоваться")
    data = validate_token(token)
    return await service.get_user_by_id(session, data.user_id)


def user_has_roles(roles: list[Role]):
    def check_roles(current_user: Annotated[User, Depends(get_current_user)]) -> bool:
        if current_user.role not in roles:
            raise ForbiddenError
        return True

    return check_roles
