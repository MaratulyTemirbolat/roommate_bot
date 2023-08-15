# Aiogram
from aiogram.fsm.state import (
    StatesGroup,
    State,
)


GENDERS = {
    "мужской": "M",
    "женский": "F",
}


CITIES = {
    "алматы": 1
}

DISTRICTS = {
    "турксибский": 7,
    "наурызбайский": 6,
    "жетысуский": 5,
    "бостандыкский": 4,
    "ауэзовский": 3,
    "алмалинский": 2,
    "алатауский": 1,
}

DISTRICTS_IDS = {
    1: "Алатауский",
    2: "Алмалинский",
    3: "Ауэзовский",
    4: "Бостандыкский",
    5: "Жетысуский",
    6: "Наурызбайский",
    7: "Турксибский"
}


class UsersSearchSteps(StatesGroup):
    """Class for following the steps for authorization."""

    GET_PREFERED_GENDER = State()
    GET_PREFERED_MAX_BUDJET = State()
    GET_PREFERED_CITY = State()
    GET_PREFERED_DISTRICTS = State()
