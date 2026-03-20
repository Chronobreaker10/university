from __future__ import annotations

from typing import TypeVar, Generic, Sequence, Callable

from pydantic import BaseModel
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import Base

T = TypeVar("T", bound=Base)


class BaseDAO(Generic[T]):
    Model: type[T]

    @classmethod
    async def create(cls, session: AsyncSession, data: BaseModel) -> T:
        data_dict = data.model_dump(exclude_unset=True)
        new_model = cls.Model(**data_dict)
        session.add(new_model)
        await session.flush()
        return new_model

    @classmethod
    async def add_all(cls, session: AsyncSession, data: list[BaseModel]) -> Sequence[T]:
        new_models = [cls.Model(**item.model_dump(exclude_unset=True)) for item in data]
        session.add_all(new_models)
        await session.flush()
        return new_models

    @classmethod
    async def get_one_by_id(cls, session: AsyncSession, model_id: int) -> T | None:
        result = await session.get(cls.Model, model_id)
        return result

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, filters: BaseModel) -> T:
        filter_dict = filters.model_dump(exclude_unset=True)
        query = select(cls.Model).filter_by(**filter_dict).limit(1)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def find_by_filter(cls, session: AsyncSession, filters: BaseModel) -> Sequence[T]:
        filter_dict = filters.model_dump(exclude_unset=True)
        query = select(cls.Model).filter_by(**filter_dict)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_all(cls, session: AsyncSession) -> Sequence[T]:
        query = select(cls.Model)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def update(cls, session: AsyncSession, model: Model, data: BaseModel):
        data_dict = data.model_dump(exclude_unset=True)
        for key, value in data_dict.items():
            setattr(model, key, value)
        await session.flush()

    @classmethod
    async def update_by_filter(cls, session: AsyncSession, filters: BaseModel, data: BaseModel) -> Callable[[], int]:
        filter_dict = filters.model_dump(exclude_unset=True)
        data_dict = data.model_dump(exclude_unset=True)
        stmt = update(cls.Model).filter_by(**filter_dict).values(**data_dict)
        result = await session.execute(stmt)
        await session.flush()
        return result.rowcount

    @classmethod
    async def delete(cls, session: AsyncSession, model: Model):
        await session.delete(model)

    @classmethod
    async def delete_by_filter(cls, session: AsyncSession, filters: BaseModel | None) -> Callable[[], int]:
        if filters is None:
            stmt = delete(cls.Model)
        else:
            filter_dict = filters.model_dump(exclude_unset=True)
            stmt = delete(cls.Model).filter_by(**filter_dict)
        result = await session.execute(stmt)
        await session.flush()
        return result.rowcount
