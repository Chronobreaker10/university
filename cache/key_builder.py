import hashlib
from typing import Callable, Any, Tuple, Dict, Optional
from fastapi import Response, Request
from sqlalchemy.ext.asyncio import AsyncSession


def common_key_builder(
    func: Callable[..., Any],
    namespace: str = "",
    *,
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
) -> str:
    exclude = (AsyncSession,)
    cache_kw = {}
    for key, value in kwargs.items():
        if not isinstance(value, exclude):
            cache_kw[key] = value
    cache_key = hashlib.md5(
        f"{func.__module__}:{func.__name__}:{args}:{cache_kw}".encode()
    ).hexdigest()
    return f"{namespace}:{cache_key}"
