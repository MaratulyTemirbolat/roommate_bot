# Python
from datetime import datetime

# Third party
from pydantic import BaseModel


class City(BaseModel):
    id: int
    name: str
    datetime_created: datetime
    is_deleted: bool


class District(BaseModel):
    id: int
    name: str
    city: City
    is_deleted: bool
    datetime_created: datetime
