from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.dao.base import BaseDAO
from core.models import Student, Major
from sqlalchemy import select, event, update


class StudentDAO(BaseDAO[Student]):
    Model = Student

    @classmethod
    async def get_all_with_major(cls, session: AsyncSession, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        query = select(cls.Model).options(joinedload(cls.Model.major)).filter_by(**filter_dict)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_one_by_id_with_major(cls, session: AsyncSession, student_id: int):
        query = select(cls.Model).options(joinedload(cls.Model.major)).filter_by(id=student_id).limit(1)
        result = await session.execute(query)
        return result.scalar_one_or_none()


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
