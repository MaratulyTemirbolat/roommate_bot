# Python
from typing import (
    Optional,
    List,
)
from datetime import datetime

# Third party
from pydantic import BaseModel

# Project
from core.models.locations import District


class CustomUserList(BaseModel):
    id: int
    email: str
    phone: str
    first_name: str
    telegram_username: Optional[str]
    telegram_user_id: Optional[int]
    gender: str
    is_active_account: bool
    month_budjet: int
    comment: Optional[str]
    photo: Optional[str]
    districts: List[District]
    is_superuser: bool
    is_deleted: bool
    datetime_created: datetime


class CustomUserDetail(CustomUserList):
    access: str
    refresh: str
