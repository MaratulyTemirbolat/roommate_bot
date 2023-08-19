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
        text="Найти людей!",
        callback_data="finish_distr_choice_btn"
    )
    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup()


def get_finish_districts_registration() -> InlineKeyboardBuilder:
    """Get own made keyboard for districts choice confirmation."""
    keyboard_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text="Подтвердить выбранный список районов",
        callback_data="registration_confirm_distr_btn"
    )
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()


def get_next_detail_user_keyboard() -> InlineKeyboardBuilder:
    """Get own made keyboard for user."""
    keyboard_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text="Просмотреть",
        callback_data="view_user_detail_btn"
    )
    keyboard_builder.button(
        text="Следущющий человек",
        callback_data="view_user_next_btn"
    )
    keyboard_builder.button(
        text="Завершить",
        callback_data="view_user_finish_btn"
    )
    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup()


def get_account_change_distr_keyboard() -> InlineKeyboardBuilder:
    """Get own made keyboard fur user."""
    keyboard_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text="Изменить выбранные районы",
        callback_data="change_coosen_distr_btn"
    )
    return keyboard_builder.as_markup()
