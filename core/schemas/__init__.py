__all__ = [
    'StudentRead',
    'StudentFilterByID',
    'StudentUpdate',
    'StudentCreate',
    'StudentFilterParams',
    'StudentFilter',
    'MajorCreate',
    'MajorFilter',
    'MajorRead',
    'UserCreate',
    'UserRead',
    'UserAuth',
    'TokenData',
    'Token',
    'PaginationParams',
    'StudentResponse',
    'MajorResponse',
    'DefaultResponse',
    'UserRegister'
]

from .major import MajorCreate, MajorFilter, MajorRead, MajorResponse
from .student import (StudentRead, StudentFilterByID, StudentUpdate, StudentCreate, StudentFilterParams, StudentFilter,
                      StudentResponse)
from .user import UserCreate, UserRead, UserAuth, TokenData, Token, UserRegister
from .pagination import PaginationParams, DefaultResponse
