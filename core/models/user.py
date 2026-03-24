from __future__ import annotations

from enum import Enum

from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column

from core.models.annotations import int_pk, str_uniq
from core.models import Base


class Role(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    USER = "user"


class User(Base):
    id: Mapped[int_pk]
    phone_number: Mapped[str_uniq]
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str_uniq]
    hashed_password: Mapped[str] = mapped_column(String(100))
    role: Mapped[Role] = mapped_column(default=Role.USER, server_default=text("'USER'"))

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}first_name={self.email}"
