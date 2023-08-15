# Aiogram
from aiogram.fsm.state import (
    StatesGroup,
    State,
)


class RegistrationSteps(StatesGroup):
    """Class for following the steps to register."""

    GET_EMAIL = State()
    GET_PHONE = State()
    GET_FIRST_NAME = State()
    GET_GENDER = State()
    GET_MONTH_BUDJET = State()
    GET_PASSWORD = State()
    GET_COMMENT = State()


class AuthorizationSteps(StatesGroup):
    """Class for following the steps for authorization."""

    GET_EMAIL_PHONE_USERNAME = State()
    GET_PASSWORD = State()
