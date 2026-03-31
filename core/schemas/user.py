from typing import Annotated

from pydantic import BaseModel, Field, EmailStr, ConfigDict, model_validator
from pydantic_extra_types.phone_numbers import PhoneNumber
from enum import Enum


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    phone_number: Annotated[
        PhoneNumber,
        Field(title="Номер телефона", description="Номер телефона в международном формате, начинающийся с '+'")
    ]
    first_name: Annotated[
        str, Field(min_length=1, max_length=50, title="Имя", description="Имя, от 1 до 50 символов")
    ]
    last_name: Annotated[
        str, Field(min_length=1, max_length=50, title="Фамилия", description="Фамилия, от 1 до 50 символов")
    ]
    email: Annotated[EmailStr, Field(title="Email", description="Электронная почта")]


class UserCreate(UserBase):
    hashed_password: Annotated[
        str, Field(min_length=5, max_length=100, title="Пароль", description="Пароль, от 5 до 100 символов")
    ]


class UserRegister(UserCreate):
    repeat_password: Annotated[
        str, Field(min_length=5, max_length=100, title="Пароль", description="Пароль, от 5 до 100 символов")
    ]

    @model_validator(mode='after')
    def check_passwords(self):
        if self.hashed_password != self.repeat_password:
            raise ValueError('Пароли не совпадают')
        return self


class UserAuth(BaseModel):
    email: Annotated[EmailStr, Field(title="Email", description="Электронная почта")]
    password: Annotated[
        str, Field(min_length=5, max_length=100, title="Пароль", description="Пароль, от 5 до 100 символов")
    ]


class TokenData(BaseModel):
    user_id: Annotated[int, Field(ge=1, le=1000, title="ID", description="ID")]


class TokenType(str, Enum):
    ACCESS = "access"


class Token(BaseModel):
    token: str
    type: TokenType = TokenType.ACCESS


class UserRead(UserBase):
    id: Annotated[int, Field(ge=1, le=1000, title="ID", description="ID")]
