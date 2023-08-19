# Python
from typing import (
    Sequence,
)

# Aiogram
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_preferred_sex_keyboard() -> ReplyKeyboardBuilder:
    """Get Keyboard related to the sex of the user."""
    keyboard_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    keyboard_builder.button(text="Мужской")
    keyboard_builder.button(text="Женский")
    keyboard_builder.button(text="Не важно")
    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_keyboard_by_data_sequence(
    data: Sequence[str],
    extra_sequence: Sequence[str] = [],
    one_time_keyboard: bool = False,
    resize_keyboard: bool = True,
) -> ReplyKeyboardBuilder:
    """Get Keyboard related to the sex of the user."""
    keyboard_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    obj: str
    for obj in extra_sequence:
        keyboard_builder.button(
            text=obj.capitalize()
        )
    for obj in data:
        keyboard_builder.button(
            text=obj.capitalize()
        )
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup(
        resize_keyboard=resize_keyboard,
        one_time_keyboard=one_time_keyboard,
    )
