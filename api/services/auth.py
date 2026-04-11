from __future__ import annotations

import hashlib
import json

from fastapi.encoders import jsonable_encoder
from fastapi import Depends
from pydantic import create_model
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from redis.asyncio.client import Pipeline

from core.config import settings
from core.dao import UserDAO
from core.errors import UnauthorizedError, InvalidCredentialsError
from core.models import User
from core.redis import get_redis
from redis.asyncio import Redis
from core.schemas import UserCreate
from core.security.auth import get_password_hash, verify_password, create_access_token, create_refresh_token
from core.broker import broker
from datetime import datetime, timezone
from core.database import db_helper


class AuthService:
    def __init__(self,
                 session: Annotated[AsyncSession | None, Depends(db_helper.get_session())],
                 redis: Annotated[Redis, Depends(get_redis)]):
        self.session = session
        self.redis = redis

    async def register_user(self, data: UserCreate) -> int:
        new_user = data.model_copy(update={"hashed_password": get_password_hash(data.hashed_password)})
        result = await UserDAO.create(self.session, new_user)
        await self.session.commit()
        await broker.publish(message=new_user.email, queue="user-registered")
        return result

    async def logout_user(self, user: User, token: str) -> bool:
        refresh_token_hash = hashlib.sha256((token + settings.security.secret_key).encode()).hexdigest()
        key = f"{settings.redis.prefix}:{settings.security.refresh_token_key}:{refresh_token_hash}"
        user_data = await self.redis.get(key)
        if not user_data:
            raise UnauthorizedError
        user_id = json.loads(user_data).get("user_id")
        set_key = f"{settings.redis.prefix}:user:{user_id}:refresh_tokens"
        if not user_id or user_id != user.id:
            raise UnauthorizedError
        async with self.redis.pipeline(transaction=True) as pipe:
            res = await pipe.delete(key).srem(set_key, refresh_token_hash).execute()
        if not res:
            raise UnauthorizedError
        return True

    async def logout_all_devices(self, user: User, token: str) -> bool:
        # logout_result = await self.logout_user(user, token)
        # if not logout_result:
        #     return False
        # pattern = f"{settings.redis.prefix}:{settings.security.refresh_token_key}:{user.id}:*"
        # async with self.redis.pipeline(transaction=True) as pipe:
        #     async for key in self.redis.scan_iter(match=pattern):
        #         pipe.delete(key)
        #     result = await pipe.execute()
        set_key = f"{settings.redis.prefix}:user:{user.id}:refresh_tokens"
        token_hashes = await self.redis.smembers(set_key)
        keys_to_delete = [f"{settings.redis.prefix}:{settings.security.refresh_token_key}:{token_hash}" for token_hash
                          in token_hashes]
        keys_to_delete.append(set_key)
        result = await self.redis.delete(*keys_to_delete)
        if result:
            return True
        return False

    async def login_user(self, email: str, password: str):
        UserEmail = create_model("UserEmail", email=(str, ...))
        user = await UserDAO.find_one_or_none(self.session, UserEmail(email=email))
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError
        access_token, refresh_token = await self.generate_tokens(user.id)
        return access_token, refresh_token, user

    async def generate_tokens(self, user_id: int) -> tuple[str, str]:
        access_token = create_access_token(data={"sub": str(user_id)})
        refresh_token = create_refresh_token()
        refresh_token_hash = hashlib.sha256((refresh_token + settings.security.secret_key).encode()).hexdigest()
        # key = f"{settings.redis.prefix}:{settings.security.refresh_token_key}:{user_id}:{refresh_token_hash}"
        key = f"{settings.redis.prefix}:{settings.security.refresh_token_key}:{refresh_token_hash}"
        set_key = f"{settings.redis.prefix}:user:{user_id}:refresh_tokens"
        user_data = json.dumps(jsonable_encoder({"user_id": user_id, "created": datetime.now(timezone.utc)}))
        async with self.redis.pipeline(transaction=True) as pipe:
            await pipe.set(key, user_data, ex=(settings.security.refresh_token_expires_days * 24 * 60 * 60)).sadd(
                set_key, refresh_token_hash).execute()
        return access_token, refresh_token

    async def refresh_tokens(self, token: str):
        refresh_token_hash = hashlib.sha256((token + settings.security.secret_key).encode()).hexdigest()
        # pattern = f"{settings.redis.prefix}:{settings.security.refresh_token_key}:*:{refresh_token_hash}"
        # first_key = None
        # async for key in self.redis.scan_iter(match=pattern):
        #     first_key = key
        #     break
        # if not first_key:
        #     raise UnauthorizedError
        key = f"{settings.redis.prefix}:{settings.security.refresh_token_key}:{refresh_token_hash}"
        user_data = await self.redis.get(key)
        if not user_data:
            raise UnauthorizedError
        user_id = json.loads(user_data).get("user_id")
        if not user_id:
            raise UnauthorizedError
        set_key = f"{settings.redis.prefix}:user:{user_id}:refresh_tokens"
        async with self.redis.pipeline(transaction=True) as pipe:
            res = await pipe.delete(key).srem(set_key, refresh_token_hash).execute()
        if res:
            access_token, refresh_token = await self.generate_tokens(user_id)
        else:
            raise UnauthorizedError
        return access_token, refresh_token
