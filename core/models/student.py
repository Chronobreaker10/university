from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.annotations import int_pk, str_uniq
from core.models import Base

if TYPE_CHECKING:
    from core.models import Major


class Student(Base):
    id: Mapped[int_pk]
    phone_number: Mapped[str_uniq]
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    date_of_birth: Mapped[date]
    email: Mapped[str_uniq]
    address: Mapped[str] = mapped_column(Text)
    enrollment_year: Mapped[int] = mapped_column(Integer, default=2010)
    course: Mapped[int] = mapped_column(Integer, default=1)
    special_notes: Mapped[str | None] = mapped_column(Text)
    major_id: Mapped[int] = mapped_column(Integer, ForeignKey("majors.id", ondelete="CASCADE"))
    major: Mapped["Major"] = relationship(back_populates="students")

    def __repr__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"first_name={self.first_name!r},"
                f"last_name={self.last_name!r})")
