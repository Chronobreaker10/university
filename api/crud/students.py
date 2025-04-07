from __future__ import annotations

from typing import Sequence

from json_db_lite import JSONDatabase
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Student
from core.schemas import StudentRead, StudentCreate

db = JSONDatabase('students.json')


def json_to_dict_list():
    return db.get_all_records()


def add_student(data: dict):
    data['date_of_birth'] = data['date_of_birth'].strftime('%Y-%m-%d')
    db.add_records(data)
    return True


def update_student(upd_filter: dict, new_data: dict):
    db.update_record_by_key(upd_filter, new_data)
    return True


def delete_student(key: str, value: int):
    db.delete_record_by_key(key, value)
    return True


async def find_all_students(session: AsyncSession, **filters) -> Sequence[Student]:
    result = await session.scalars(select(Student).options(joinedload(Student.major)).filter_by(**filters))
    return result.all()


async def find_student_by_id(session: AsyncSession, student_id: int) -> Student | None:
    result = await session.execute(select(Student).options(joinedload(Student.major)).where(Student.id == student_id))
    return result.scalar_one_or_none()


async def create_student(session: AsyncSession, student: StudentCreate) -> Student:
    result = Student(**student.model_dump())
    session.add(result)
    await session.commit()
    return result
