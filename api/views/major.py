import math
from typing import Annotated

from fastapi import APIRouter, Depends, status, Query, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession

import api.services.major as service
from core.database import db_helper
from core.schemas import MajorCreate, MajorResponse, MajorFilter
from core.schemas.major import MajorRead

router = APIRouter(prefix='/majors', tags=['Специальности'])


@router.get("/", summary="Получить список всех специальностей", response_model=MajorResponse)
async def get_all_majors(session: Annotated[AsyncSession, Depends(db_helper.get_session())],
                         major_filter: Annotated[MajorFilter, Query()]):
    majors, total_count = await service.get_majors_by_filter(session, major_filter)
    return MajorResponse(majors=[MajorRead.model_validate(major) for major in majors],
                         total_count=total_count, next_page_url=None, prev_page_url=None)


@router.get("/{major_id}", summary="Получить информацию о специальности по ID", response_model=MajorRead)
async def get_one_major_by_id(session: Annotated[AsyncSession, Depends(db_helper.get_session())],
                              major_id: Annotated[int, Path(ge=1, le=1000, title="ID", description="ID")]):
    return await service.get_major_by_id(session, major_id)


@router.post("/", summary="Создать новую специальность", response_model=MajorRead, status_code=status.HTTP_201_CREATED)
async def add_major(session: Annotated[AsyncSession, Depends(db_helper.get_session())], major: MajorCreate):
    return await service.create_major(session, major)


@router.put("/{major_id}", summary="Обновить информацию о специальности", response_model=MajorRead)
async def update_major(session: Annotated[AsyncSession, Depends(db_helper.get_session())],
                       major_id: Annotated[int, Path(ge=1, le=1000, title="ID", description="ID")],
                       new_major: MajorCreate):
    return await service.update_major(session, major_id, new_major)


@router.put("/", summary="Обновить информацию о специальности по названию")
async def update_major_by_name(session: Annotated[AsyncSession, Depends(db_helper.get_session())],
                               major_name: Annotated[
                                   str, Query(min_length=2, max_length=50, title="Название факультета")],
                               new_major: MajorCreate):
    result = await service.update_majors_by_name(session, major_name, new_major)
    return {
        "message": f"Обновлено {result} специальностей"
    }


@router.delete("/{major_id}", summary="Удалить специальность по ID", status_code=status.HTTP_204_NO_CONTENT)
async def delete_major(session: Annotated[AsyncSession, Depends(db_helper.get_session())],
                       major_id: Annotated[int, Path(ge=1, le=1000, title="ID", description="ID")]):
    await service.delete_major(session, major_id)
    return {
        "message": f"Специальность с ID {major_id} успешно удален"
    }
