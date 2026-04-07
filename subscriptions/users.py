from typing import Annotated

from faststream import Depends
from faststream.rabbit import RabbitRouter
from sqlalchemy.ext.asyncio import AsyncSession

from core.dao import UserDAO
from core.database import db_helper
from core.schemas import UserRead
from utils.send_email import send_verify_email

router = RabbitRouter(prefix="user_")


@router.subscriber("verify_email")
async def verify_email(user_id: int, session: Annotated[AsyncSession, Depends(db_helper.get_session())]):
    user = await UserDAO.get_one_by_id(session, user_id)
    if user is not None:
        await send_verify_email(UserRead.model_validate(user))
