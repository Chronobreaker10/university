from functools import cache
from core.config import settings
from redis.asyncio import Redis


@cache
def get_redis() -> Redis:
    return Redis(host=settings.redis.host, port=settings.redis.port, db=settings.redis.db)