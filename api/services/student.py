from sqlalchemy.ext.asyncio import AsyncSession

from core.dao import StudentDAO
from core.errors import NotFoundError
from core.models import Student
from core.schemas import StudentFilter, StudentCreate, StudentResponse


async def get_students_by_filter(session: AsyncSession, student_filter: StudentFilter) \
        -> tuple[list[Student], int]:
    offset = (student_filter.page - 1) * student_filter.per_page
    if student_filter.search:
        total_count, students = await StudentDAO.search_all_with_count(session, student_filter.search, offset,
                                                                       student_filter.per_page)
        print(total_count)
    else:
        filters = StudentFilter.model_validate(
            student_filter.model_dump(exclude={'page', 'per_page', 'search'}, exclude_unset=True))
        students = await StudentDAO.get_all_with_major(session, filters, offset, student_filter.per_page)
        total_count = await StudentDAO.get_count(session, filters)
    return list(students), total_count


async def get_student_by_id(session: AsyncSession, student_id: int) -> Student:
    result = await StudentDAO.get_one_by_id_with_major(session, student_id)
    if result is None:
        raise NotFoundError
    return result


async def create_student(session: AsyncSession, data: StudentCreate) -> int:
    result = await StudentDAO.create(session, data)
    return result


async def update_student(session: AsyncSession, student_id: int, data: StudentCreate) -> Student:
    student = await get_student_by_id(session, student_id)
    await StudentDAO.update(session, student, data)
    return student


async def delete_student(session: AsyncSession, student_id: int) -> None:
    student = await get_student_by_id(session, student_id)
    await StudentDAO.delete(session, student)
