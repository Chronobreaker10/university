import httpx
import asyncio

API_URL = "http://127.0.0.1:8000"


async def get_all_students():
    async with httpx.AsyncClient() as client:
        response = await client.get('http://127.0.0.1:8000/students')
        return response.json()


async def get_student_by_id(student_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f'http://127.0.0.1:8000/students/{student_id}')
        return response.json()


async def get_students_by_course(course: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f'http://127.0.0.1:8000/students', params={'course': course})
        return response.json()


async def test_api():
    students = await get_all_students()
    print(students)
    student = await get_student_by_id(1)
    print(student)
    students = await get_students_by_course(1)
    print(students)


if __name__ == '__main__':
    asyncio = asyncio.run(test_api())
