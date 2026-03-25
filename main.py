from __future__ import annotations

import pathlib
from contextlib import asynccontextmanager
from random import randint
from typing import Annotated, AsyncGenerator

import uvicorn
from fastapi import FastAPI, Query, Path, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis
from starlette.middleware.sessions import SessionMiddleware

import api.crud.students as student_crud
from core.config import settings
from core.database import db_helper
from core.errors import BaseError
from core.schemas import StudentRead, StudentUpdate, StudentFilterByID, StudentFilterParams
from pages import router as page_router
from api.views import router as api_router
from utils import json_to_dict_list

parent_dir = pathlib.Path(__file__).parent
data_dir = parent_dir / 'students.json'


@asynccontextmanager
async def lifespan(current_app: FastAPI) -> AsyncGenerator[None, None]:
    redis = Redis(host=settings.redis.host, port=settings.redis.port,
                  db=settings.cache.db_name)
    FastAPICache.init(RedisBackend(redis), prefix=settings.cache.prefix)
    yield
    await db_helper.dispose()


app = FastAPI(lifespan=lifespan)
frontend = FastAPI()
api = FastAPI(default_response_class=ORJSONResponse)
api.include_router(api_router)
frontend.include_router(page_router)
app.add_middleware(SessionMiddleware, secret_key=settings.security.secret_key)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/api", api)
app.mount("/pages", frontend)


@app.get("/")
async def home_page():
    return {"message": "Привет, Мир!!!"}


@app.get('/json/students', response_model=list[StudentRead])
async def get_students(params: Annotated[StudentFilterParams, Query()]):
    students = json_to_dict_list(data_dir)
    for student in students:
        student['id'] = student['student_id']
        student['major_name'] = student['major']
        student['major_id'] = randint(1, 100)
    response = []
    if students:
        response = students
        if params.course:
            response = [student for student in response if student['course'] == params.course]
        if params.major:
            response = [student for student in response if student['major'].lower() == params.major.lower()]
        if params.enrollment_year:
            response = [student for student in response if student['enrollment_year'] == params.enrollment_year]
    return response


@app.get('/json/students/{student_id}', response_model=StudentRead)
async def get_student_by_id(student_id: Annotated[int, Path(ge=1, le=1000, title="ID", description="ID")]):
    students = json_to_dict_list(data_dir)
    for student in students:
        student['id'] = student['student_id']
        student['major_name'] = student['major']
        student['major_id'] = randint(1, 100)
    response = {}
    if students:
        filtered_students = [student for student in students if student['student_id'] == student_id]
        if filtered_students:
            response = filtered_students[0]
    return response


@app.post('/json/students')
async def create_student(student: StudentRead):
    data = student.model_dump()
    del data["id"]
    del data["major_name"]
    del data["major_id"]
    data["student_id"] = student.id
    data["major"] = student.major_name
    add = student_crud.add_student(student.model_dump())
    if add:
        return {"message": "Студент успешно добавлен!"}
    else:
        raise HTTPException(status_code=400, detail="Ошибка при добавлении студента")


@app.put('/json/students/{student_id}')
async def update_student(student_filter: StudentFilterByID, student: StudentUpdate):
    update = student_crud.update_student(student_filter.model_dump(), student.model_dump())
    if update:
        return {"message": "Студент успешно обновлен!"}
    else:
        raise HTTPException(status_code=400, detail="Ошибка при обновлении информации о студенте")


@app.delete('/json/students/{student_id}')
async def delete_student(student_filter: StudentFilterByID):
    del_student = student_crud.delete_student('student_id', student_filter.student_id)
    if del_student:
        return {"message": "Студент успешно удален!"}
    else:
        raise HTTPException(status_code=400, detail="Ошибка при удалении студента")


@api.exception_handler(BaseError)
async def not_found_exception_handler(request, exc: BaseError):
    return JSONResponse(
        status_code=exc.code,
        content={"message": exc.message}
    )


@frontend.exception_handler(BaseError)
async def redirect_exception_handler(request: Request, exc: BaseError):
    request.session["flashed_message"] = {
        "type": "error",
        "text": exc.message
    }
    if exc.flash:
        form_data = await request.form()
        request.session["flashed_data"] = {
            key: value for key, value in form_data.items()
        }
    url = request.url_for(exc.redirect_to) if exc.redirect_to else request.url
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


@frontend.exception_handler(RequestValidationError)
async def redirect_exception_handler(request: Request, exc: RequestValidationError):
    request.session["flashed_message"] = {
        "type": "error",
        "text": "Проверьте правильность введенных данных!"
    }
    form_data = await request.form()
    request.session["flashed_data"] = {
        key: value for key, value in form_data.items()
    }
    return RedirectResponse(url=request.url, status_code=status.HTTP_303_SEE_OTHER)


if __name__ == '__main__':
    uvicorn.run(app, host=settings.run.host, port=settings.run.port, reload=True)
