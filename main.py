from __future__ import annotations

from typing import Annotated
from fastapi import FastAPI, Query, Path
from utils import json_to_dict_list
from core.schemas import StudentRead, StudentUpdate, StudentFilterByID
import api.crud.students as student_crud
import pathlib
import uvicorn
from api.views.students import router as students_router

parent_dir = pathlib.Path(__file__).parent
data_dir = parent_dir / 'students.json'

app = FastAPI()

app.include_router(students_router)


@app.get("/")
def home_page():
    return {"message": "Привет, Хабр!"}


@app.get('/json/students', response_model=list[StudentRead])
async def get_students(
        course: Annotated[int | None, Query(ge=1, le=5, title="Курс", description="Курс")] = None,
        major: Annotated[str | None, Query(max_length=100, title="Специальность", description="Специальность")] = None,
        enrollment_year: Annotated[
            int | None, Query(gt=2010, lt=2025, title="Год поступления", description="Год поступления")] = None,
):
    students = json_to_dict_list(data_dir)
    response = []
    if students:
        response = students
        if course:
            response = [student for student in response if student['course'] == course]
        if major:
            response = [student for student in response if student['major'].lower() == major.lower()]
        if enrollment_year:
            response = [student for student in response if student['enrollment_year'] == enrollment_year]
    return response


@app.get('/json/students/{student_id}', response_model=StudentRead)
async def get_student_by_id(student_id: Annotated[int, Path(ge=1, le=1000, title="ID", description="ID")]):
    students = json_to_dict_list(data_dir)
    response = {}
    if students:
        filtered_students = [student for student in students if student['student_id'] == student_id]
        if filtered_students:
            response = filtered_students[0]
    return response


@app.post('/json/students')
async def create_student(student: StudentRead):
    add = student_crud.add_student(student.model_dump())
    if add:
        return {"message": "Студент успешно добавлен!"}
    else:
        return {"message": "Ошибка при добавлении студента"}


@app.put('/json/students/{student_id}')
async def update_student(student_filter: StudentFilterByID, student: StudentUpdate):
    update = student_crud.update_student(student_filter.model_dump(), student.model_dump())
    if update:
        return {"message": "Студент успешно обновлен!"}
    else:
        return {"message": "Ошибка при обновлении студента"}


@app.delete('/json/students/{student_id}')
async def delete_student(student_filter: StudentFilterByID):
    del_student = student_crud.delete_student('student_id', student_filter.student_id)
    if del_student:
        return {"message": "Студент успешно удален!"}
    else:
        return {"message": "Ошибка при удалении студента"}


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000, reload=True)
