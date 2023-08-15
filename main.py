# Python
from logging import (
    basicConfig,
    INFO,
)
from typing import (
    Tuple,
    Dict,
    Any,
)

# Third part
from asyncio import run
from aioredis import Redis

# Aiogram
from aiogram import (
    Bot,
    Dispatcher,
    F,
)
from aiogram.filters import (
    CommandStart,
    Command,
)
from aiogram.fsm.storage.redis import RedisStorage

# Project
from core.utils.commands import set_commands
from core.handlers.basics import get_start
from core.handlers.auhts.handlers import (
    register_handler_cmd,
    get_email_registration,
    get_phone_registration,
    get_fake_phone_registration,
    get_first_name_registration,
    get_gender_registration,
    get_month_budjet_registration,
    get_password_registration,
    get_comment_registration,
    login_handle_cmd,
    get_email_phone_login,
    get_password_login,
)
from core.handlers.auhts.usersearchhandler import (
    handle_search_cmd,
    get_preferred_gender,
    get_preferred_max_budjet,
    get_preferred_city,
    get_preferred_districts,
)
from core.handlers.auhts.callback import (
    select_registration,
    finish_district_selection,
)
from core.settings import settings
from core.utils.fsm.auths.states_auths import (
    RegistrationSteps,
    AuthorizationSteps,
)
from core.utils.fsm.auths.states_search import UsersSearchSteps
from core.filters.contact_filter import IsOwnerContact
from core.middlewares.redismiddleware import RedisMiddleware


async def start_bot(
    bot: Bot,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    await set_commands(bot=bot)
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

    redis: Redis = Redis(
        host="localhost",
        port=6379,
        db=0
    )

    dp: Dispatcher = Dispatcher(storage=RedisStorage(redis=redis))

    # Middleware registers
    dp.message.middleware.register(middleware=RedisMiddleware(redis=redis))

    # Main system registers
    dp.startup.register(callback=start_bot)
    dp.shutdown.register(callback=stop_bot)

    # Message registrations
    dp.message.register(get_start, CommandStart())
    dp.message.register(
        handle_search_cmd,
        F.text == "Поиск людей"
    )
    dp.message.register(
        handle_search_cmd,
        Command(commands="find_roommates")
    )
    dp.message.register(
        get_preferred_gender,
        UsersSearchSteps.GET_PREFERED_GENDER,
        F.text.strip()
    )
    dp.message.register(
        get_preferred_max_budjet,
        UsersSearchSteps.GET_PREFERED_MAX_BUDJET,
        F.text.strip()
    )
    dp.message.register(
        get_preferred_city,
        UsersSearchSteps.GET_PREFERED_CITY,
        F.text.strip()
    )
    dp.message.register(
        get_preferred_districts,
        UsersSearchSteps.GET_PREFERED_DISTRICTS,
        F.text.strip()
    )
    dp.message.register(
        register_handler_cmd,
        F.text == "Зарегистрироваться"
    )
    dp.message.register(
        get_password_login,
        AuthorizationSteps.GET_PASSWORD,
        F.text.strip()
    )
    dp.message.register(
        get_email_phone_login,
        AuthorizationSteps.GET_EMAIL_PHONE_USERNAME,
        F.text.strip()
    )
    dp.message.register(login_handle_cmd, Command(commands="login"))
    dp.message.register(
        login_handle_cmd,
        F.text == "Авторизоваться"
    )
    dp.message.register(register_handler_cmd, Command(commands="register"))
    dp.message.register(
        get_email_registration,
        RegistrationSteps.GET_EMAIL
    )
    dp.message.register(
        get_phone_registration,
        RegistrationSteps.GET_PHONE,
        F.contact,
        IsOwnerContact()
    )
    dp.message.register(
        get_fake_phone_registration,
        RegistrationSteps.GET_PHONE,
        F.contact
    )
    dp.message.register(
        get_first_name_registration,
        RegistrationSteps.GET_FIRST_NAME
    )
    dp.message.register(
        get_gender_registration,
        RegistrationSteps.GET_GENDER
    )
    dp.message.register(
        get_month_budjet_registration,
        RegistrationSteps.GET_MONTH_BUDJET
    )
    dp.message.register(
        get_password_registration,
        RegistrationSteps.GET_PASSWORD
    )
    dp.message.register(
        get_comment_registration,
        RegistrationSteps.GET_COMMENT
    )

    # Callbacks registration
    dp.callback_query.register(
        finish_district_selection,
        F.data == "finish_distr_choice_btn"
    )
    dp.callback_query.register(
        select_registration,
        F.data == "continue_registration_btn"
    )

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    run(start())
