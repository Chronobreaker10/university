from typing import Annotated

from fastapi import APIRouter, Request, Depends
from fastapi import status, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

import api.services.major as major_service
from api.dependencies.user import get_current_user
from api.views.major import get_all_majors
from core.database import db_helper
from core.schemas import MajorCreate, MajorRead, UserRead, MajorResponse, FlashMessage, MessageStatus

router = APIRouter(prefix="/majors", tags=["Специальности"])
templates = Jinja2Templates(directory="templates")


@router.get("/", name="majors.index")
def get_majors(request: Request, data: Annotated[MajorResponse, Depends(get_all_majors)],
               current_user: Annotated[UserRead, Depends(get_current_user)]):
    message = request.session.pop("flashed_message", "")
    return templates.TemplateResponse("majors/index.html",
                                      {"request": request, "response": data, "title": "Специальности",
                                       "current_user": current_user, "message": message})


@router.get("/create", name="majors.create")
def create_major(request: Request, current_user: Annotated[UserRead, Depends(get_current_user)]):
    return templates.TemplateResponse("majors/create.html",
                                      {"request": request, "title": "Добавить специальность",
                                       "current_user": current_user})


@router.post("/", name="majors.post")
async def post_major(request: Request, major: Annotated[MajorCreate, Form()],
                     session: Annotated[AsyncSession, Depends(db_helper.get_session())],
                     current_user: Annotated[UserRead, Depends(get_current_user)]):
    major_id = await major_service.create_major(session, major)
    request.session["flashed_message"] = FlashMessage(status=MessageStatus.SUCCESS,
                                                      text=f"Специальность {major_id} успешно добавлена!").model_dump()
    return RedirectResponse(url=request.url_for("majors.index"), status_code=status.HTTP_303_SEE_OTHER)
