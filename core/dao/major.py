from core.dao.base import BaseDAO
from core.models import Major


class MajorDAO(BaseDAO[Major]):
    Model = Major
    SEARCH_FIELDS = ['major_name']
