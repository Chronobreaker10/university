from typing import Annotated

from fastapi import Request, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

import api.services.auth as auth_service
import api.services.user as service
from core.config import settings
from core.database import db_helper
from core.errors import UnauthorizedError, ForbiddenError
from core.models import Role
from core.models import User
from core.security.auth import validate_token


async def get_current_user(session: Annotated[AsyncSession, Depends(db_helper.get_session())],
                           request: Request) -> User:
    access_token = request.cookies.get(settings.security.access_token_cookie_name)
    if not access_token:
        raise UnauthorizedError
    data = validate_token(access_token)
    return await service.get_user_by_id(session, data.user_id)


def user_has_roles(roles: list[Role]):
    def check_roles(current_user: Annotated[User, Depends(get_current_user)]) -> bool:
        if current_user.role not in roles:
            raise ForbiddenError
        return True

    return check_roles
