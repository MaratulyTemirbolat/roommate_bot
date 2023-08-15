# Aiogram
from aiogram.filters.callback_data import CallbackData


class DistrictInfo(CallbackData, prefix="district"):
    id: int
    name: str
