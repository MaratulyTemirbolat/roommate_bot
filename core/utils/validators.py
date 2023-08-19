# Python
from re import (
    compile,
    fullmatch,
    match,
)
from typing import Tuple

EMAIL_REG_TEMPLATE = \
    r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"

MAX_MONTH_BUDJET = 10000000

PHONE_REG_TEMPLATE = "^\\+?[1-9][0-9]{7,14}$"


def is_valid_phone_number(phone: str) -> bool:
    return True if match(
        pattern=PHONE_REG_TEMPLATE,
        string=phone
    ) else False


def is_valid_email(email: str) -> bool:
    """Validate provided email."""
    return True if fullmatch(
        pattern=compile(EMAIL_REG_TEMPLATE),
        string=email
    ) else False


def is_convertable_str_to_int(
    inp_str: str,
    variable_name: str
) -> Tuple[bool, str]:
    try:
        _: int = int(inp_str)
        return (True, "",)
    except ValueError:
        return (
            False,
            f"Ошибка! {variable_name.capitalize()} не является числом"
        )


def is_positive_number(
    numb: str,
    variable_name: str
) -> Tuple[bool, str]:
    """Validate is the number positive or not."""
    return (True, "") \
        if int(numb) > 0 \
        else (
            False,
            f"Ошибка! {variable_name.capitalize()} "
            "должен быть положительным и отличным от нуля"
        )


def is_money_limit(
    numb: str,
    variable_name: str
) -> Tuple[bool, str]:
    """Validate whether the limit is or not."""
    num: int = int(numb)
    return (True, "") \
        if num < MAX_MONTH_BUDJET \
        else (
            False,
            f"Ошибка! {variable_name.capitalize()} "
            "превысил лимит в 10 миллионов. Нужно указать меньшуу сумму!"
        )
