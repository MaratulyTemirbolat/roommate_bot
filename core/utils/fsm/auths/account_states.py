# Aiogram
from aiogram.fsm.state import (
    StatesGroup,
    State,
)


class PersonalAccountSteps(StatesGroup):
    """Class for following the steps to register."""

    CHANGE_DISTRICTS_STATE = State()
