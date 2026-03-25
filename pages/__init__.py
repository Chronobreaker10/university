from fastapi import APIRouter

from pages.students import router as students_router
from pages.auth import router as auth_router
from pages.majors import router as majors_router

router = APIRouter(tags=["Frontend"])

router.include_router(students_router)
router.include_router(auth_router)
router.include_router(majors_router)
