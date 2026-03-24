from sqlalchemy.exc import IntegrityError
from typing import Sequence

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.dao.base import BaseDAO
from core.models import Student, Major
from sqlalchemy import select, event, update, or_, func
from core.errors import StudentAlreadyExistsError


class StudentDAO(BaseDAO[Student]):
    Model = Student
    SEARCH_FIELDS = ['phone_number', 'first_name', 'last_name', 'email', 'address']

    @classmethod
    async def get_all_with_major(cls, session: AsyncSession, filters: BaseModel, offset: int, limit: int) \
            -> Sequence[Student]:
        filter_dict = filters.model_dump(exclude_unset=True)
        query = select(cls.Model).options(joinedload(cls.Model.major)).filter_by(**filter_dict).offset(offset).limit(
            limit)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def search_all_with_count(cls, session: AsyncSession, keyword: str, offset: int, limit: int) \
            -> tuple[int, Sequence[Student]]:
        query = select(cls.Model).options(joinedload(cls.Model.major))
        conditions = []
        for field in cls.SEARCH_FIELDS:
            if field in cls.Model.__table__.columns:
                conditions.append(getattr(cls.Model, field).ilike(f"%{keyword}%"))
        query = query.where(or_(*conditions))
        result = await session.execute(query.offset(offset).limit(limit))
        count_query = await session.scalar(select(func.count()).select_from(query.subquery()))
        return count_query, result.scalars().all()

    @classmethod
    async def get_one_by_id_with_major(cls, session: AsyncSession, student_id: int):
        query = select(cls.Model).options(joinedload(cls.Model.major)).filter_by(id=student_id).limit(1)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def create(cls, session: AsyncSession, data: BaseModel) -> Model:
        try:
            return await super().create(session, data)
        except IntegrityError as e:
            raise StudentAlreadyExistsError from e


@event.listens_for(Student, "after_insert")
def receive_after_insert(mapper, connection, target):
    connection.execute(
        update(Major).where(Major.id == target.major_id).values(count_students=Major.count_students + 1)
    )


@event.listens_for(Student, "after_delete")
def receive_after_delete(mapper, connection, target):
    connection.execute(
        update(Major).where(Major.id == target.major_id).values(count_students=Major.count_students - 1)
    )
