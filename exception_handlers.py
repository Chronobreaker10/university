from fastapi import status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi_csrf_protect.exceptions import CsrfProtectError

from core.errors import BaseError, InvalidCredentials, UnauthorizedError
from core.schemas import FlashMessage, MessageStatus
from core.logger import app_errors_logger
from main import api, frontend, app


# @api.exception_handler(BaseError)
# async def api_exception_handler(_, exc: BaseError):
#     return JSONResponse(
#         status_code=exc.code,
#         content={"message": exc.message}
#     )


