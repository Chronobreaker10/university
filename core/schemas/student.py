from __future__ import annotations

from datetime import datetime, date
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, EmailStr, field_validator, field_serializer, ConfigDict, \
    computed_field
from pydantic_extra_types.phone_numbers import PhoneNumber

from core.schemas.major import MajorRead


class Major(str, Enum):
    informatics = "Информатика"
    economics = "Экономика"
    law = "Право"
    medicine = "Медицина"
    engineering = "Инженерия"
    languages = "Языки"
    history = "История"
    ecology = "Экология"
    math = "Математика"
    psychology = "Психология"
    biology = "Биология"


class StudentFilterByID(BaseModel):
    student_id: Annotated[int, Field(ge=1, le=1000, title="ID", description="ID")]


class StudentUpdate(BaseModel):
    major: Annotated[
        Major, Field(title="Специальность студента", description="Специальность студента")
    ]
    course: Annotated[
        int, Field(ge=1, le=5, title="Курс студента", description="Курс должен быть в диапазоне от 1 до 5")
    ]


class StudentCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    phone_number: Annotated[
        PhoneNumber,
        Field(title="Номер телефона студента", description="Номер телефона в международном формате, начинающийся с '+'")
    ]
    first_name: Annotated[
        str, Field(min_length=1, max_length=50, title="Имя", description="Имя студента, от 1 до 50 символов")
    ]
    last_name: Annotated[
        str, Field(min_length=1, max_length=50, title="Фамилия", description="Фамилия студента, от 1 до 50 символов")
    ]
    date_of_birth: Annotated[
        date, Field(title="Дата рождения", description="Дата рождения студента в формате ГГГГ-ММ-ДД")
    ]
    email: Annotated[EmailStr, Field(title="Email", description="Электронная почта студента")]
    address: Annotated[
        str, Field(min_length=10, max_length=200, title="Адрес", description="Адрес студента, от 1 до 100 символов")
    ]
    enrollment_year: Annotated[
        int, Field(ge=2010, title="Год поступления", description="Год поступления должен быть не меньше 2010")
    ]
    major_id: Annotated[
        int, Field(title="Специальность студента", description="Специальность студента")
    ]
    course: Annotated[
        int, Field(ge=1, le=5, title="Курс студента", description="Курс должен быть в диапазоне от 1 до 5")
    ]
    special_notes: Annotated[
        str | None, Field(max_length=500, title="Примечание студента", description="Примечание, не более 500 символов")
    ] = None

    @field_validator("date_of_birth")
    def validate_date_of_birth(cls, values: date):
        if values and values >= datetime.now().date():
            raise ValueError('Дата рождения должна быть в прошлом')
        return values

    @field_serializer("phone_number")
    def serialize_phone_number(self, value: PhoneNumber):
        return value[4:]


class StudentRead(StudentCreate):
    id: Annotated[int, Field(ge=1, le=1000, title="ID", description="ID")]
    # major_name: Annotated[
    #     str,
    #     Field(min_length=1, max_length=50, title="Специальность",
    #           description="Специальность студента, от 1 до 50 символов")
    # ]
    major: Annotated[MajorRead, Field(exclude=True)]

    @computed_field
    @property
    def major_name(self) -> str:
        return self.major.major_name


class StudentFilterParams(BaseModel):
    course: Annotated[int | None, Field(ge=1, le=5, title="Курс", description="Курс")] = None
    major: Annotated[str | None, Field(title="Специальность", description="Специальность")] = None
    enrollment_year: Annotated[
        int | None, Field(gt=2010, lt=2025, title="Год поступления", description="Год поступления")] = None


class PaginationParams(BaseModel):
    page: int = Field(ge=1, title="Страница", description="Номер страницы", default=1)
    per_page: int = Field(ge=1, le=100, title="Количество элементов на странице",
                          description="Количество элементов на странице", default=2)
    search: Annotated[str, Field(title="Поиск", description="Поиск")] = ""


class StudentFilter(PaginationParams):
    course: Annotated[int | None, Field(ge=1, le=5, title="Курс", description="Курс")] = None
    major_id: Annotated[int | None, Field(title="Специальность", description="Специальность")] = None
    enrollment_year: Annotated[
        int | None, Field(gt=2010, lt=2025, title="Год поступления", description="Год поступления")] = None


class StudentResponse(BaseModel):
    students: Annotated[list[StudentRead], Field(title="Список студентов", description="Список студентов")]
    total_count: Annotated[
        int, Field(ge=0, title="Общее количество студентов", description="Общее количество студентов")]
    prev_page_url: Annotated[str | None, Field(title="Предыдущая страница", description="URL предыдущей страницы")]
    next_page_url: Annotated[str | None, Field(title="Следующая страница", description="URL следующей страницы")]
    majors: Annotated[list[MajorRead], Field(title="Список специальностей", description="Список специальностей")]
