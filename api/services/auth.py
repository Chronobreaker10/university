from __future__ import annotations

import hashlib
import json

from fastapi.encoders import jsonable_encoder
from pydantic import create_model
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.dao import UserDAO
from core.errors import UnauthorizedError, InvalidCredentialsError
from core.models import User
from core.redis import get_redis
from core.schemas import UserCreate
from core.security.auth import get_password_hash, verify_password, create_access_token, create_refresh_token
from datetime import datetime, timezone


async def register_user(session: AsyncSession, data: UserCreate) -> int:
    new_user = data.model_copy(update={"hashed_password": get_password_hash(data.hashed_password)})
    result = await UserDAO.create(session, new_user)
    await session.commit()
    return result


async def logout_user(user: User, token: str) -> bool:
    refresh_token_hash = hashlib.sha256((token + settings.security.secret_key).encode()).hexdigest()
    redis = get_redis()
    key = f"{settings.redis.prefix}:{settings.security.refresh_token_key}:{user.id}:{refresh_token_hash}"
    user_data = await redis.get(key)
    if not user_data:
        raise UnauthorizedError
    user_id = json.loads(user_data).get("user_id")
    if not user_id or user_id != user.id:
        raise UnauthorizedError
    res = await redis.delete(key)
    if not res:
        raise UnauthorizedError
    return True


async def login_user(session: AsyncSession, email: str, password: str):
    UserEmail = create_model("UserEmail", email=(str, ...))
    user = await UserDAO.find_one_or_none(session, UserEmail(email=email))
    if not user or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError
    access_token, refresh_token = await generate_tokens(user.id)
    return access_token, refresh_token, user


async def generate_tokens(user_id: int) -> tuple[str, str]:
    access_token = create_access_token(data={"sub": str(user_id)})
    refresh_token = create_refresh_token()
    refresh_token_hash = hashlib.sha256((refresh_token + settings.security.secret_key).encode()).hexdigest()
    redis = get_redis()
    key = f"{settings.redis.prefix}:{settings.security.refresh_token_key}:{user_id}:{refresh_token_hash}"
    user_data = json.dumps(jsonable_encoder({"user_id": user_id, "created": datetime.now(timezone.utc)}))
    await redis.set(key, user_data, ex=(settings.security.refresh_token_expires_days * 24 * 60 * 60))
    return access_token, refresh_token


async def refresh_tokens(token: str):
    refresh_token_hash = hashlib.sha256((token + settings.security.secret_key).encode()).hexdigest()
    redis = get_redis()
    pattern = f"{settings.redis.prefix}:{settings.security.refresh_token_key}:*:{refresh_token_hash}"
    first_key = None
    async for key in redis.scan_iter(match=pattern):
        first_key = key
        break
    if not first_key:
        raise UnauthorizedError
    user_data = await redis.get(first_key)
    if not user_data:
        raise UnauthorizedError
    user_id = json.loads(user_data).get("user_id")
    if not user_id:
        raise UnauthorizedError
    res = await redis.delete(first_key)
    if res:
        access_token, refresh_token = await generate_tokens(user_id)
    else:
        raise UnauthorizedError
    return access_token, refresh_token
