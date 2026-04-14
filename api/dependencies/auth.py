from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from api.services.auth import AuthService
from typing import Annotated
from fastapi import Depends

from core.database import db_helper
from core.redis import get_redis


def get_auth_service(session: Annotated[AsyncSession, Depends(db_helper.get_session())],
                     redis: Annotated[Redis, Depends(get_redis)]):
    return AuthService(session, redis)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
