from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
import api.crud.students as crud
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.models import Student
from core.schemas import StudentRead, StudentCreate
from api.dependencies.student import query_params, get_student_by_id

router = APIRouter(prefix='/students', tags=['Студенты'])


@router.get('/', summary="Получить список всех студентов", response_model=list[StudentRead])
async def get_all_students(session: Annotated[AsyncSession, Depends(get_session)],
                           params: Annotated[dict, Depends(query_params)]):
    return await crud.find_all_students(session, **params)


@router.get('/{student_id}', summary="Получить информацию о студенте по ID", response_model=StudentRead)
async def get_one_student_by_id(student: Annotated[Student, Depends(get_student_by_id)]):
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Студент с таким ID не найден")
    response = StudentRead(**student.to_dict(), major_name=student.major.major_name)
    return response


@router.post('/', summary="Создать нового студента", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
async def add_student(session: Annotated[AsyncSession, Depends(get_session)], student: StudentCreate):
    response = await crud.create_student(session, student)
    return response
