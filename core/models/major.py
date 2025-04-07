from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import text, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base, int_pk, str_uniq

if TYPE_CHECKING:
    from core.models import Student


class Major(Base):
    id: Mapped[int_pk]
    major_name: Mapped[str_uniq]
    major_description: Mapped[str | None] = mapped_column(Text)
    count_students: Mapped[int] = mapped_column(default=0, server_default=text('0'))
    students: Mapped[list[Student]] = relationship(back_populates="major")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, major_name={self.major_name!r})"
