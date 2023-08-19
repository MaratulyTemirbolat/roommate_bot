# Python
from typing import Optional

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
    is_registered_user: Optional[bytes] = None,
    is_active_account: Optional[bytes] = 0
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
        if is_active_account and int(is_active_account) == 1:
            keyboard_builder.button(
                text="Поиск людей"
            )
            keyboard_builder.button(
                text="Просмотреть личные данные"
            )
            keyboard_builder.button(
                text="Деактивировать личный аккаунт"
            )
        elif is_active_account and int(is_active_account) == 0:
            keyboard_builder.button(
                text="Активировать личный аккаунт"
            )
        keyboard_builder.button(
            text="Выйти из аккаунта"
        )
        keyboard_builder.adjust(2, 2, 1)
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

no_photo_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Без фото"
            )
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Загрузите фотографию или нажмите 'Без фото'"
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
