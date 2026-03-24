from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped

from utils import camel_case_to_snake_case
from core.models.annotations import created_at, updated_at


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{camel_case_to_snake_case(cls.__name__)}s"

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
