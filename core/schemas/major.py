from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class MajorCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    major_name: Annotated[
        str, Field(min_length=1, max_length=50, title="Название",
                   description="Название специальности, от 1 до 50 символов")
    ]
    major_description: Annotated[
        str, Field(max_length=500, title="Описание",
                   description="Описание специальности, от 1 до 500 символов")
    ] = ""
    count_students: Annotated[
        int, Field(ge=0, lt=10000, title="Количество студентов",
                   description="Количество студентов с этой специальности")
    ] = 0


class MajorRead(MajorCreate):
    id: Annotated[int, Field(ge=1, le=1000, title="ID", description="ID")]


class MajorFilter(BaseModel):
    major_name: Annotated[
        str | None, Field(min_length=1, max_length=50, title="Название",
                   description="Название специальности, от 1 до 50 символов")
    ] = None
