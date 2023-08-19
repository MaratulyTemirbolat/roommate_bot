# python
from typing import (
    Tuple,
    List,
    Dict,
    Any,
)

# aigram
from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeDefault,
)


async def set_commands(
    bot: Bot,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Set all the commands for bot working."""
    commands: List[BotCommand] = [
        BotCommand(
            command="start",
            description="Запустить бота"
        ),
        BotCommand(
            command="register",
            description="Регистрация пользователя"
        ),
        BotCommand(
            command="login",
            description="Авторизация пользователя"
        ),
        BotCommand(
            command="find_roommates",
            description="Поиск людей"
        ),
        BotCommand(
            command="view_account",
            description="Просмотреть личные профиль"
        )
    ]
    await bot.set_my_commands(
        commands=commands,
        scope=BotCommandScopeDefault()
    )
