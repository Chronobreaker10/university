from __future__ import annotations

from typing import Annotated

from fastapi import Query, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_session
from core.dao import StudentDAO


def query_params(course: Annotated[int | None, Query(ge=1, le=5, title="Курс", description="Курс")] = None,
                 major: Annotated[
                     str | None, Query(max_length=100, title="Специальность", description="Специальность")] = None,
                 enrollment_year: Annotated[
                     int | None, Query(gt=2010, lt=2025, title="Год поступления",
                                       description="Год поступления")] = None):
    params = {
        "course": course,
        "major": major,
        "enrollment_year": enrollment_year
    }
    return {
        key: value for key, value in params.items() if value is not None
    }


async def get_student_by_id(session: Annotated[AsyncSession, Depends(get_session())],
                            student_id: Annotated[int, Path(ge=1, le=1000, title="ID", description="ID")]):
    return await StudentDAO.get_one_by_id(session, student_id)
