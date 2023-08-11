# Third party
from decouple import config

# Aiogram
from aiogram import (
    Bot,
    Dispatcher,
    executor,
)
from aiogram.types import Message


bot: Bot = Bot(token=config("BOT_TOKEN", cast=str))
dp: Dispatcher = Dispatcher(bot=bot)


@dp.message_handler(commands=["start"])
async def start_handler(message: Message) -> None:
    await message.answer(
        text=f"{message.from_user.first_name}, добро пожаловать в roommate app"
    )


@dp.message_handler()
async def wrong_handler(message: Message) -> None:
    await message.reply(text="Извините, я вас не понимаю.")


if __name__ == "__main__":
    executor.start_polling(dispatcher=dp)
