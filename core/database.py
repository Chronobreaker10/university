from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine

from .config import settings

log = logging.getLogger(__name__)


class DatabaseHelper:

    def __init__(self, url: str,
                 echo: bool = False,
                 echo_pool: bool = False,
                 pool_size: int = 5,
                 max_overflow: int = 10,
                 ) -> None:
        self.engine: AsyncEngine = create_async_engine(url=url,
                                                       echo=echo,
                                                       echo_pool=echo_pool,
                                                       pool_size=pool_size,
                                                       max_overflow=max_overflow)
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(bind=self.engine,
                                                                                    expire_on_commit=False,
                                                                                    autoflush=False, autocommit=False)

    def get_session(self, isolation_level: str | None = None, commit: bool = True):
        async def yield_session() -> AsyncSession:
            async with self.session_factory() as session:
                try:
                    if isolation_level:
                        await session.execute(text(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}"))
                    yield session
                    if commit:
                        await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    log.error(e)

        return yield_session


db_helper = DatabaseHelper(
    url=settings.db.url,
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow
)
