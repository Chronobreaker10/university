from sqlalchemy.ext.asyncio import AsyncSession

from core.dao import StudentDAO
from core.errors import NotFoundError
from core.models import Student
from core.schemas import StudentFilter, StudentCreate


async def get_students_by_filter(session: AsyncSession, student_filter: StudentFilter) -> list[Student]:
    return await StudentDAO.get_all_with_major(session, student_filter)


async def get_student_by_id(session: AsyncSession, student_id: int) -> Student:
    result = await StudentDAO.get_one_by_id_with_major(session, student_id)
    if result is None:
        raise NotFoundError
    return result


async def create_student(session: AsyncSession, data: StudentCreate) -> Student:
    result = await StudentDAO.create(session, data)
    return result


async def update_student(session: AsyncSession, student_id: int, data: StudentCreate) -> Student:
    student = await get_student_by_id(session, student_id)
    await StudentDAO.update(session, student, data)
    return student


async def delete_student(session: AsyncSession, student_id: int) -> None:
    student = await get_student_by_id(session, student_id)
    await StudentDAO.delete(session, student)
