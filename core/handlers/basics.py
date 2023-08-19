# Python
from typing import (
    Tuple,
    Dict,
    Any,
    Optional,
)

# Third party
from aioredis import Redis

# Aiogram
from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

# Project
from core.keyboards.reply.reply import get_main_reply_keyboard


async def get_start(
    message: Message,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle START command function."""
    is_registered: Optional[Any] = await redis_cli.get(
        name=message.from_user.id
    )
    await state.clear()
    await bot.send_message(
        chat_id=message.from_user.id,
        text=f"Привет <b>{message.from_user.first_name}</b>. "
        "Рад тебя видеть в нашем чате\r\n",
        reply_markup=get_main_reply_keyboard(
            is_registered_user=is_registered,
            is_active_account=await redis_cli.get(
                name=f"{message.from_user.id}_is_active_account"
            )
        )
    )


async def handle_unclear_request(
    message: Message
) -> None:
    """Handle unclear command."""
    await message.answer(
        text="Извините, я вас не понимаю.\r\n"
        "Пожалуйста, выберите одну из комманд или нажмите /start"
    )
