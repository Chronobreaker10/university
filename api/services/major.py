from __future__ import annotations

from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from core.dao import MajorDAO
from core.schemas import MajorFilter, MajorCreate
from core.models import Major
from core.errors import NotFoundError


async def get_majors_by_filter(session: AsyncSession, major_filter: MajorFilter | None) -> tuple[list[Major], int]:
    if major_filter is not None and major_filter.major_name is not None:
        total_count, majors = await MajorDAO.search_all_with_count(session, major_filter.major_name)
    else:
        majors = await MajorDAO.find_by_filter(session)
        total_count = await MajorDAO.get_count(session)
    return list(majors), total_count


async def get_major_by_id(session: AsyncSession, major_id: int) -> Major:
    result = await MajorDAO.get_one_by_id(session, major_id)
    if result is None:
        raise NotFoundError
    return result


async def create_major(session: AsyncSession, data: MajorCreate) -> Major:
    result = await MajorDAO.create(session, data)
    return result


async def update_major(session: AsyncSession, major_id: int, data: MajorCreate) -> Major:
    major = await get_major_by_id(session, major_id)
    await MajorDAO.update(session, major, data)
    return major


async def update_majors_by_name(session: AsyncSession, name: str, data: MajorCreate) -> Callable[[], int]:
    result = await MajorDAO.update_by_filter(session, MajorFilter(major_name=name), data)
    return result


async def delete_major(session: AsyncSession, major_id: int):
    major = await get_major_by_id(session, major_id)
    await MajorDAO.delete(session, major)
