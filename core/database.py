from __future__ import annotations

from datetime import datetime
from typing import Annotated

from sqlalchemy import func, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

from core.errors import DatabaseError
from .config import settings

engine = create_async_engine(settings.DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


def get_session(isolation_level: str | None = None, commit: bool = True):
    async def yield_session() -> AsyncSession:
        async with async_session_maker() as session:
            try:
                if isolation_level:
                    await session.execute(text(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}"))
                yield session
                if commit:
                    await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                print(e)
                raise DatabaseError from e
    return yield_session


int_pk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(default=datetime.now(), server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(
    default=datetime.now(), server_default=func.now(), onupdate=datetime.now)]
str_uniq = Annotated[str, mapped_column(unique=True)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
