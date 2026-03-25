import math
from typing import Annotated

from fastapi import APIRouter, Depends, status, Query, Path, Request, BackgroundTasks
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

import api.services.student as service
import api.services.major as major_service
from api.dependencies.user import user_has_roles
from core.database import db_helper
from core.models import Role
from core.schemas import StudentRead, StudentCreate, StudentFilter, StudentResponse, MajorRead
from cache import common_key_builder

router = APIRouter(prefix='/students', tags=['Студенты'])

ACCESS_ROLES = [Role.ADMIN, Role.TEACHER, Role.SUPER_ADMIN]


@router.post("/", summary="Создать нового студента", status_code=status.HTTP_201_CREATED)
async def add_student(session: Annotated[AsyncSession, Depends(db_helper.get_session())], student: StudentCreate,
                      background_tasks: BackgroundTasks):
    response = await service.create_student(session, student)
    background_tasks.add_task(FastAPICache.clear, namespace="students")
    return {
        "message": f"Студент {response} успешно создан"
    }


@router.get("/", summary="Получить список всех студентов", response_model=StudentResponse,
            dependencies=[Depends(user_has_roles(ACCESS_ROLES))])
@cache(expire=60, key_builder=common_key_builder, namespace="students")
#
async def get_all_students(session: Annotated[AsyncSession, Depends(db_helper.get_session())],
                           student_filter: Annotated[StudentFilter, Query()], request: Request) -> StudentResponse:
    prev_url, next_url = None, None
    students, total_count = await service.get_students_by_filter(session, student_filter)
    if student_filter.page > 1 and total_count > 0:
        params = student_filter.model_dump(exclude={'page'}, exclude_unset=True)
        params["page"] = student_filter.page - 1
        prev_url = str(request.url_for('students.index').include_query_params(**params))
    total_pages = math.ceil(total_count / student_filter.per_page)
    if student_filter.page < total_pages:
        params = student_filter.model_dump(exclude={'page'}, exclude_unset=True)
        params["page"] = student_filter.page + 1
        next_url = str(request.url_for('students.index').include_query_params(**params))
    majors, count = await major_service.get_majors_by_filter(session, None)
    return StudentResponse(students=[StudentRead.model_validate(student) for student in students],
                           total_count=total_count, next_page_url=next_url, prev_page_url=prev_url, majors=[
            MajorRead.model_validate(major) for major in majors
        ])


@router.get("/{student_id}", summary="Получить информацию о студенте по ID", response_model=StudentRead)
@cache(expire=60, key_builder=common_key_builder, namespace="students")
async def get_one_student_by_id(session: Annotated[AsyncSession, Depends(db_helper.get_session())],
                                student_id: Annotated[int, Path(ge=1, le=1000, title="ID", description="ID")]):
    return await service.get_student_by_id(session, student_id)
