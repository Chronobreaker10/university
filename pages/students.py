from typing import Annotated

from fastapi import APIRouter, Request, Depends
from fastapi import status, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

import api.services.student as student_service
from api.dependencies.user import get_current_user
from api.views.major import get_all_majors
from api.views.students import get_all_students
from core.database import db_helper
from core.schemas import StudentResponse, StudentCreate, UserRead, FlashMessage, MessageStatus, MajorResponse

router = APIRouter(prefix="/students", tags=["Студенты"])
templates = Jinja2Templates(directory="templates")


@router.get("/", name="students.index")
def get_students(request: Request, data: Annotated[StudentResponse, Depends(get_all_students)],
                 current_user: Annotated[UserRead, Depends(get_current_user)]):
    message = request.session.pop("flashed_message", "")
    return templates.TemplateResponse("students/index.html",
                                      {"request": request, "response": data, "title": "Студенты",
                                       "current_user": current_user, "message": message})


@router.get("/create", name="students.create")
def create_student(request: Request, majors: Annotated[MajorResponse, Depends(get_all_majors)],
                   current_user: Annotated[UserRead, Depends(get_current_user)]):
    message = request.session.pop("flashed_message", "")
    return templates.TemplateResponse("students/create.html",
                                      {"request": request, "title": "Добавить студента", "majors": majors.majors,
                                       "current_user": current_user, "message": message})


@router.post("/create", name="students.post")
async def post_student(request: Request, student: Annotated[StudentCreate, Form()],
                       session: Annotated[AsyncSession, Depends(db_helper.get_session())],
                       current_user: Annotated[UserRead, Depends(get_current_user)]):
    student = await student_service.create_student(session, student)
    request.session["flashed_message"] = FlashMessage(status=MessageStatus.SUCCESS,
                                                      text=f"Студент {student} успешно добавлен!").model_dump()
    return RedirectResponse(url=request.url_for("students.index"), status_code=status.HTTP_303_SEE_OTHER)
