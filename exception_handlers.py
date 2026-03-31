from fastapi import status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi_csrf_protect.exceptions import CsrfProtectError

from core.errors import BaseError, InvalidCredentials, UnauthorizedError
from core.schemas import FlashMessage, MessageStatus
from core.logger import app_errors_logger
from main import api, frontend, app


@api.exception_handler(BaseError)
async def api_exception_handler(_, exc: BaseError):
    return JSONResponse(
        status_code=exc.code,
        content={"message": exc.message}
    )


@frontend.exception_handler(BaseError)
async def redirect_exception_handler(request: Request, exc: BaseError):
    request.session["flashed_message"] = jsonable_encoder(FlashMessage(status=MessageStatus.ERROR,
                                                                       text="Проверьте правильность введенных данных!"))
    if exc.flash:
        form_data = await request.form()
        request.session["flashed_data"] = {
            key: value for key, value in form_data.items()
        }
    url = request.url_for(exc.redirect_to) if exc.redirect_to else request.url
    if isinstance(exc, UnauthorizedError):
        request.session.pop("current_user", None)
        url = url.include_query_params(next=request.url.path)
    if isinstance(exc, InvalidCredentials):
        url = url.include_query_params(next=request.query_params.get("next"))
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


@frontend.exception_handler(RequestValidationError)
async def redirect_validation_handler(request: Request, _):
    request.session["flashed_message"] = jsonable_encoder(FlashMessage(status=MessageStatus.ERROR,
                                                                       text="Проверьте правильность введенных данных!"))
    form_data = await request.form()
    request.session["flashed_data"] = {
        key: value for key, value in form_data.items()
    }
    return RedirectResponse(url=request.url, status_code=status.HTTP_303_SEE_OTHER)


@app.exception_handler(Exception)
async def base_exception_handler(_, exc: Exception):
    app_errors_logger.error(exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Произошла непредвиденная ошибка"}
    )


@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(_, exc: CsrfProtectError):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.message})
