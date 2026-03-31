from __future__ import annotations

import pathlib
from contextlib import asynccontextmanager
from random import randint
from typing import Annotated, AsyncGenerator

import uvicorn
from fastapi import FastAPI, Query, Path, HTTPException, Request, Depends
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_csrf_protect import CsrfProtect
from redis.asyncio import Redis
from starlette.middleware.sessions import SessionMiddleware

import api.crud.students as student_crud
from api.views import router as api_router
from core.config import settings
from core.database import db_helper
from core.schemas import StudentRead, StudentUpdate, StudentFilterByID, StudentFilterParams
from pages import router as page_router
from utils import json_to_dict_list
from datetime import datetime
import time
from core.logger import access_logger

parent_dir = pathlib.Path(__file__).parent
data_dir = parent_dir / 'students.json'


@asynccontextmanager
async def lifespan(current_app: FastAPI) -> AsyncGenerator[None, None]:
    redis = Redis(host=settings.redis.host, port=settings.redis.port,
                  db=settings.cache.db_name)
    FastAPICache.init(RedisBackend(redis), prefix=settings.cache.prefix)
    yield
    await db_helper.dispose()


async def clear_session(request: Request):
    yield
    request.session.pop("flashed_data", None)


app = FastAPI(lifespan=lifespan)
frontend = FastAPI(dependencies=[Depends(clear_session)])
api = FastAPI(default_response_class=ORJSONResponse)
api.include_router(api_router)
frontend.include_router(page_router)
app.add_middleware(SessionMiddleware, secret_key=settings.security.secret_key)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/api", api)
app.mount("/pages", frontend)


@app.middleware("http")
async def log_request(request, call_next):
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    response = await call_next(request)
    process_time = time.time() - start_time
    timestamp = datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0300")
    log_message = (f'{client_ip} - - [{timestamp}] "{request.method} {request.url.path} '
                   f'HTTP/{request.scope.get("http_version", "1.1")}" {response.status_code} '
                   f'- "-" "{request.headers.get("user-agent", "-")}" {process_time:.3f}s')
    access_logger.info(log_message)
    return response


@CsrfProtect.load_config
def get_csrf_config():
    return settings.csrf


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


if __name__ == '__main__':
    uvicorn.run(app, host=settings.run.host, port=settings.run.port, reload=True)
