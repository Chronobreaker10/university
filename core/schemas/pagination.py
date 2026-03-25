from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field


class PaginationResponse(BaseModel):
    total_count: Annotated[
        int, Field(ge=0, title="Общее количество элементов'", description="Общее количество элементов на странице")]
    prev_page_url: Annotated[str | None, Field(title="Предыдущая страница", description="URL предыдущей страницы")]
    next_page_url: Annotated[str | None, Field(title="Следующая страница", description="URL следующей страницы")]


class PaginationParams(BaseModel):
    page: int = Field(ge=1, title="Страница", description="Номер страницы", default=1)
    per_page: int = Field(ge=1, le=100, title="Количество элементов на странице",
                          description="Количество элементов на странице", default=2)
    search: Annotated[str, Field(title="Поиск", description="Поиск")] = ""
