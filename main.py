# Python
from asyncio import run
from logging import (
    basicConfig,
    INFO,
)
from typing import (
    Tuple,
    Dict,
    Any,
)

# Aiogram
from aiogram import (
    Bot,
    Dispatcher,
)

# Project
from core.handlers.basics import get_start
from core.settings import settings


async def start_bot(
    bot: Bot,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    await bot.send_message(
        chat_id=settings.bot.admin_id,
        text="Бот успешно запущен!"
    )


async def stop_bot(
    bot: Bot,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    await bot.send_message(
        chat_id=settings.bot.admin_id,
        text="Бот остановился!"
    )


async def start() -> None:
    basicConfig(
        level=INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s -"
               "(%(filename)s). %(funcName)s(%(lineno)d) - %(message)s"
    )
    bot: Bot = Bot(
        token=settings.bot.bot_token,
        parse_mode="HTML"
    )

    # Dispatcher это объект, который занимается получением Updates
    dp: Dispatcher = Dispatcher()
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    dp.message.register(get_start)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    run(start())
