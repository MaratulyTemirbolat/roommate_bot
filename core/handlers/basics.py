# Python
from typing import (
    Tuple,
    Dict,
    Any,
)

# Aiogram
from aiogram import Bot
from aiogram.types import Message


async def get_start(
    message: Message,
    bot: Bot,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    await bot.send_message(
        chat_id=message.from_user.id,
        text=f"<b>Привет {message.from_user.first_name}. Рад тебя видеть</b>"
    )
    await message.answer(
        text=f"<s>Привет {message.from_user.first_name}. Рад тебя видеть</s>"
    )
    await message.reply(
        text=f"<tg-spoiler>Привет\
{message.from_user.first_name}. Рад тебя видеть</tg-spoiler>"
    )
