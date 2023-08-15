# Python
from typing import (
    Optional,
    Any,
)

# Aiogram
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder


main_options_reply_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Зарегистрироваться"
            ),
        ],
        [
            KeyboardButton(
                text="Авторизоваться"
            ),
        ],
        [
            KeyboardButton(
                text="Поиск людей"
            ),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Выберите кнопку",
    selective=True,
)


def get_main_reply_keyboard(
    is_registered_user: Optional[Any] = None
) -> ReplyKeyboardBuilder:
    """Get Keyboard related to the main user part."""
    keyboard_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    if not is_registered_user:
        keyboard_builder.button(
            text="Зарегистрироваться"
        )
        keyboard_builder.button(
            text="Авторизоваться"
        )
    elif is_registered_user:
        keyboard_builder.button(
            text="Поиск людей"
        )

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )


own_phone_number_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Отправить свой контакт",
                request_contact=True
            )
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Отправить свой номер телефона",
)

yes_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Оставить предложенное имя",
            )
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

GENDER_OPTIONS = {
    "парень": "M",
    "девушка": "F",
}
gender_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Парень"
            ),
            KeyboardButton(
                text="Девушка"
            ),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


def get_name_keyboard(name: str) -> ReplyKeyboardBuilder:
    """Get Keyboard related to the name of the user."""
    keyboard_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    keyboard_builder.button(text=f"Оставить как {name.capitalize()}")
    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )
