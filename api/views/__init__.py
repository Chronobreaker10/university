from fastapi import APIRouter

from api.views.major import router as major_router
from api.views.students import router as students_router
from api.views.users import router as user_router

router = APIRouter()

router.include_router(students_router)
router.include_router(major_router)
router.include_router(user_router)
