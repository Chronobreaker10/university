from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi_csrf_protect.exceptions import CsrfProtectError

from core.errors import BaseError, UnauthorizedError, InvalidCredentialsError, NotFoundError
from core.logger import app_errors_logger
from core.schemas import FlashMessage, MessageStatus
from main import frontend
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi import Request, status
from core.config import settings

templates = Jinja2Templates(directory="templates")


@frontend.exception_handler(Exception)
async def front_base_exception_handler(request: Request, exc: Exception):
    if settings.ENV == "dev":
        app_errors_logger.error(exc, exc_info=True)
    else:
        print(exc)
    return templates.TemplateResponse("errors/500.html", {"request": request})



@frontend.exception_handler(BaseError)
async def redirect_exception_handler(request: Request, exc: BaseError):
    if exc.flash:
        form_data = await request.form()
        request.session["flashed_data"] = {
            key: value for key, value in form_data.items()
        }
    url = request.url_for(exc.redirect_to) if exc.redirect_to else request.url
    if isinstance(exc, UnauthorizedError):
        request.session.pop("current_user", None)
        url = url.include_query_params(next=request.url.path)
    if isinstance(exc, InvalidCredentialsError):
        url = url.include_query_params(next=request.query_params.get("next"))
    request.session["flashed_message"] = jsonable_encoder(FlashMessage(status=MessageStatus.ERROR,
                                                                       text=exc.message))
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



@frontend.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return templates.TemplateResponse("errors/400.html", {"request": request})


@frontend.exception_handler(NotFoundError)
def csrf_protect_exception_handler(request: Request, exc: NotFoundError):
    return templates.TemplateResponse("errors/404.html", {"request": request})


@frontend.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        return templates.TemplateResponse("errors/404.html", {"request": request})
    raise exc