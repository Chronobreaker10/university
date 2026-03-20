from typing import Annotated

from fastapi import APIRouter, Depends, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

import api.services.student as service
from core.database import get_session
from core.schemas import StudentRead, StudentCreate, StudentFilter

router = APIRouter(prefix='/students', tags=['Студенты'])


@router.get("/", summary="Получить список всех студентов", response_model=list[StudentRead])
async def get_all_students(session: Annotated[AsyncSession, Depends(get_session())],
                           student_filter: Annotated[StudentFilter, Query()]):
    return await service.get_students_by_filter(session, student_filter)


@router.get("/{student_id}", summary="Получить информацию о студенте по ID", response_model=StudentRead)
async def get_one_student_by_id(session: Annotated[AsyncSession, Depends(get_session())],
                                student_id: Annotated[int, Path(ge=1, le=1000, title="ID", description="ID")]):
    return await service.get_student_by_id(session, student_id)


@router.post("/", summary="Создать нового студента", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
async def add_student(session: Annotated[AsyncSession, Depends(get_session())], student: StudentCreate):
    response = await service.create_student(session, student)
    return await service.get_student_by_id(session, response.id)
