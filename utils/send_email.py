from email.message import EmailMessage

import aiosmtplib
from jinja2 import Template

from core.config import settings
from core.dao.user import UserDAO
from core.database import db_helper
from core.schemas import UserRead
from core.security.auth import create_access_token


async def send_email(
        recipient: str,
        subject: str,
        body: str
):
    message = EmailMessage()
    message["From"] = settings.mail.smtp_email
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)
    message.add_alternative(body, subtype="html")

    await aiosmtplib.send(message, sender=settings.mail.smtp_email, recipients=recipient,
                          hostname=settings.mail.smtp_host,
                          port=settings.mail.smtp_port, username=settings.mail.smtp_email,
                          password=settings.mail.smtp_password, use_tls=True)


async def send_verify_email(user: UserRead):
    template = (settings.mail.templates_path / "verify_email.html").read_text(encoding="utf-8")
    verification_link = (f"http://{settings.run.host}:{settings.run.port}"
                         f"/pages/auth/verify?token={create_access_token(data={"sub": str(user.id)})}")
    content = Template(template).render({"user": user, "verification_link": verification_link})
    await send_email(user.email, "Подтверждение Email", content)


async def send_verify_email_task(
        user_id: int
):
    async with db_helper.session_factory() as session:
        user = await UserDAO.get_one_by_id(session, user_id)
        if user is not None:
            await send_verify_email(UserRead.model_validate(user))
