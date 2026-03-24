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
    'StudentResponse'
]

from .major import MajorCreate, MajorFilter, MajorRead
from .student import (StudentRead, StudentFilterByID, StudentUpdate, StudentCreate, StudentFilterParams, StudentFilter,
                      PaginationParams, StudentResponse)
from .user import UserCreate, UserRead, UserAuth, TokenData, Token
