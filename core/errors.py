from fastapi import status


class DatabaseError(Exception):
    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "При работе с базой данных произошла ошибка"


class NotFoundError(Exception):
    code = status.HTTP_404_NOT_FOUND
    message = "Запрашиваемый ресурс не найден"
