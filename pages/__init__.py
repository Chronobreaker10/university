from fastapi import APIRouter

from pages.students import router as students_router
from pages.auth import router as auth_router

router = APIRouter(prefix="/pages", tags=["Frontend"])

router.include_router(students_router)
router.include_router(auth_router)
