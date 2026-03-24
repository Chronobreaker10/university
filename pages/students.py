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
from core.schemas import StudentResponse, StudentCreate, MajorRead

router = APIRouter(prefix="/students", tags=["Студенты"], dependencies=[Depends(get_current_user)])
templates = Jinja2Templates(directory="templates")


@router.get("/", name="students.index")
def get_students(request: Request, data: Annotated[StudentResponse, Depends(get_all_students)]):
    message = request.session.pop("flashed_message", "")
    return templates.TemplateResponse("students/index.html",
                                      {"request": request, "response": data, "title": "Студенты", "message": message})


@router.get("/create", name="students.create")
def create_student(request: Request, majors: Annotated[list[MajorRead], Depends(get_all_majors)]):
    message = request.session.pop("flashed_message", "")
    return templates.TemplateResponse("students/create.html",
                                      {"request": request, "title": "Добавить студента", "majors": majors, "message": message})


@router.post("/", name="students.post")
async def post_student(request: Request, student: Annotated[StudentCreate, Form()], session: Annotated[AsyncSession, Depends(db_helper.get_session())]):
    student = await student_service.create_student(session, student)
    request.session["flashed_message"] = {
        "type": "success",
        "text": f"Студент {student.id} успешно добавлен!"
    }
    return RedirectResponse(url=request.url_for("students.index"), status_code=status.HTTP_303_SEE_OTHER)
