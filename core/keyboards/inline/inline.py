# Aiogram
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_preregister_keyboards() -> InlineKeyboardBuilder:
    """Get own made keyboard before registration."""
    keyboard_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text="Правила соглашения",
        url="https://google.com"
    )
    keyboard_builder.button(
        text="Начать регистрацию",
        callback_data="continue_registration_btn"
    )
    keyboard_builder.adjust(3)
    return keyboard_builder.as_markup()


def get_finish_districts_search() -> InlineKeyboardBuilder:
    """Get own make keyboard for districts choice finish."""
    keyboard_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text="Закончить выбор районов",
        callback_data="finish_distr_choice_btn"
    )
    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup()
