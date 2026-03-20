from __future__ import annotations

import pathlib
from random import randint
from typing import Annotated

import uvicorn
from fastapi import FastAPI, Query, Path, HTTPException
from fastapi.responses import JSONResponse

import api.crud.students as student_crud
from api.views.students import router as students_router
from api.views.major import router as major_router
from core.errors import NotFoundError
from core.schemas import StudentRead, StudentUpdate, StudentFilterByID, StudentFilterParams
from utils import json_to_dict_list

parent_dir = pathlib.Path(__file__).parent
data_dir = parent_dir / 'students.json'

app = FastAPI()

app.include_router(students_router)
app.include_router(major_router)


@app.get("/")
def home_page():
    return {"message": "Привет, Мир!"}


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


@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request, exc: NotFoundError):
    return JSONResponse(
        status_code=exc.code,
        content={"message": exc.message}
    )


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000, reload=True)
