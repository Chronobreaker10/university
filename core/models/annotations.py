from datetime import datetime, timezone
from typing import Annotated

from sqlalchemy import func
from sqlalchemy.orm import mapped_column


def get_current_dt() -> datetime:
    dt = datetime.now(tz=timezone.utc)
    return dt.replace(microsecond=0, tzinfo=None)


int_pk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(default=get_current_dt, server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(
    default=get_current_dt, server_default=func.now(), onupdate=get_current_dt)]
str_uniq = Annotated[str, mapped_column(unique=True)]
