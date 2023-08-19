# Python
from typing import (
    Tuple,
    Optional,
    Dict,
    Any,
    List,
)

# Third party
from aioredis import Redis
from pickle import (
    dumps,
    loads,
)

# Aiogram
from aiogram.types import (
    Message,
    URLInputFile,
)
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender

# Project
from core.api.services import (
    handle_patch,
    handle_get,
    handle_post,
)
from core.keyboards.inline.inline import get_account_change_distr_keyboard
from core.keyboards.reply.reply import get_main_reply_keyboard
from core.models.auths import CustomUserList
from core.utils.utils import get_user_detail_info
from core.settings import ONE_MONTH_SECONDS
from core.utils.fsm.auths.states_search import (
    DISTRICTS_IDS,
    DISTRICTS,
)


async def activate_deactivate_action(
    message: Message,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    url: str,
    jwt_token: Optional[bytes] = None,
    is_act_state: bool = False,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle user DEACTIVATION STATE."""
    response: Dict[str, Any] = await handle_patch(
        url=url,
        headers={
            "Authorization": f"JWT {jwt_token.decode()}",
        }
    )
    response_text: str = response.get("response")
    if int(response.get("status")) >= 400:
        await message.answer(
            text=f"Произошла ошибка. {response_text}",
            reply_markup=get_main_reply_keyboard(
                is_registered_user=jwt_token,
                is_active_account=await redis_cli.get(
                    name=f"{message.from_user.id}_is_active_account"
                )
            )
        )
    elif int(response.get("status")) >= 200 and int(response.get("status")) < 300:  # noqa
        await redis_cli.set(
            name=f"{message.from_user.id}_is_active_account",
            value=int(True if is_act_state else False),
            ex=ONE_MONTH_SECONDS
        )
        await message.answer(
            text=response.get("response")["response"],
            reply_markup=get_main_reply_keyboard(
                is_registered_user=jwt_token,
                is_active_account=await redis_cli.get(
                    name=f"{message.from_user.id}_is_active_account"
                )
            )
        )


async def activate_deactivate_account_handler(
    message: Message,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle user DEACTIVATION STATE."""
    await state.clear()
    jwt_token: Optional[Any] = await redis_cli.get(name=message.from_user.id)
    if not jwt_token:
        await message.answer(
            text="Извините, но вам для начала нужно авторизоваться в системе",
            reply_markup=get_main_reply_keyboard(
                is_registered_user=None
            )
        )
    elif jwt_token:
        main_url: str = "http://localhost:8000/api/v1/auths/users/"
        is_activated_state: bool = True \
            if message.text == "Активировать личный аккаунт" \
            else False

        url: str = main_url + "activate" \
            if is_activated_state \
            else main_url + "deactivate"
        await activate_deactivate_action(
            message=message,
            bot=bot,
            state=state,
            redis_cli=redis_cli,
            url=url,
            jwt_token=jwt_token,
            is_act_state=is_activated_state,
            *args,
            **kwargs
        )


async def personal_info_handler(
    message: Message,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle viewing personal account info."""
    await state.clear()
    jwt_token: Optional[bytes] = await redis_cli.get(name=message.from_user.id)
    if not jwt_token:
        await message.answer(
            text="Извините, но вам необходимо авторизоваться в системе",
            reply_markup=get_main_reply_keyboard()
        )
    elif jwt_token:
        await message.answer(
            text="Запрашиваем данные о вас..."
        )
        response: Dict[str, Any] = await handle_get(
            url="http://localhost:8000/api/v1/auths/users/personal_account",
            headers={
                "Authorization": f"JWT {jwt_token.decode()}",
            }
        )
        response_text: str = response.get("response")
        if int(response.get("status")) >= 400:
            await message.answer(
                text=f"Произошла ошибка. {response_text}",
                reply_markup=get_main_reply_keyboard(
                    is_registered_user=jwt_token,
                    is_active_account=await redis_cli.get(
                        name=f"{message.from_user.id}_is_active_account"
                    )
                )
            )
        elif int(response.get("status")) >= 200 and int(response.get("status")) < 300:  # noqa
            user: CustomUserList = CustomUserList(
                **response["response"]["data"]
            )
            await redis_cli.set(
                name=f"{message.from_user.id}_reg_districts",
                value=dumps([str(dist.id) for dist in user.districts]),
                ex=ONE_MONTH_SECONDS
            )
            await redis_cli.set(
                name=f"{message.from_user.id}_reg_districts_copy",
                value=dumps([str(dist.id) for dist in user.districts]),
                ex=int(ONE_MONTH_SECONDS/4)
            )
            async with ChatActionSender.upload_photo(
                chat_id=message.from_user.id,
                bot=bot
            ):
                img_url: str = user.photo \
                    if user.photo \
                    else "https://icon-library.com/images/no-picture-available-icon/no-picture-available-icon-20.jpg"  # noqa

                img: URLInputFile = URLInputFile(
                    url=img_url,
                    filename="user-logo.png"
                )
                await redis_cli.set(
                    name=f"{message.from_user.id}_is_active_account",
                    value=int(user.is_active_account),
                    ex=ONE_MONTH_SECONDS
                )
                await bot.send_photo(
                    chat_id=message.from_user.id,
                    photo=img,
                    caption=get_user_detail_info(user=user),
                    reply_markup=get_account_change_distr_keyboard(),
                )
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text="Можете выбрать одно из действий с пользователем или "
                    "использовать нижнее меню",
                    reply_markup=get_main_reply_keyboard(
                        is_registered_user=jwt_token,
                        is_active_account=await redis_cli.get(
                            name=f"{message.from_user.id}_is_active_account"
                        )
                    )
                )


async def logout_account_handler(
    message: Message,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle logout the system handler."""
    jwt_token: Optional[Any] = await redis_cli.get(name=message.from_user.id)
    if not jwt_token:
        await message.answer(
            text="Вы итак уже вышли со своего аккаунта",
            reply_markup=get_main_reply_keyboard(
                is_registered_user=jwt_token,
                is_active_account=await redis_cli.get(
                    name=f"{message.from_user.id}_is_active_account"
                )
            )
        )
    elif jwt_token:
        await redis_cli.delete(message.from_user.id)
        await message.answer(
            text="Вы успешно вышли из своего аккаунта",
            reply_markup=get_main_reply_keyboard()
        )


async def handle_change_user_districts_btn(
    message: Message,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle change user districts."""
    jwt_token: Optional[bytes] = await redis_cli.get(
        name=f"{message.from_user.id}"
    )
    if jwt_token:
        distr_name: str = f"{message.from_user.id}_reg_districts_copy"
        opt_distr: Optional[bytes] = await redis_cli.get(
            name=distr_name
        )
        user_distr: List[str] = loads(opt_distr) if opt_distr else []

        user_answ: str = message.text.strip().lower()

        if user_answ == "отмена":
            await state.clear()
            await message.answer(
                text="Отмена действия. Возвращаемся в главное меню.",
                reply_markup=get_main_reply_keyboard(
                    is_registered_user=jwt_token,
                    is_active_account=await redis_cli.get(
                        name=f"{message.from_user.id}_is_active_account"
                    )
                )
            )
            return None
        elif user_answ == "сохранить список":
            if len(user_distr) == 0:
                await message.answer(
                    text="Необходимо добавить хотя бы 1 район"
                )
            else:
                await message.answer(
                    text="Сохраняю список районов..."
                )
                url: str = \
                    "http://localhost:8000/api/v1/auths/users/add_districts"
                response: Dict[str, Any] = await handle_post(
                    url=url,
                    headers={
                        "Authorization": f"JWT {jwt_token.decode()}",
                    },
                    data={
                        "districts": ",".join(user_distr)
                    }
                )
                if int(response.get("status")) >= 400:
                    await message.answer(
                        text=f"Произошла ошибка. {response.get('response')}",
                        reply_markup=get_main_reply_keyboard(
                            is_registered_user=jwt_token,
                            is_active_account=await redis_cli.get(
                                name=f"{message.from_user.id}_is_active_account"  # noqa
                            )
                        )
                    )
                elif int(response.get("status")) >= 200 and int(response.get("status")) < 300:  # noqa
                    await redis_cli.set(
                        name=f"{message.from_user.id}_reg_districts",
                        value=dumps(obj=user_distr),
                        ex=ONE_MONTH_SECONDS
                    )
                    await message.answer(
                        text="Ваши районы были успешно обновлены",
                        reply_markup=get_main_reply_keyboard(
                            is_registered_user=jwt_token,
                            is_active_account=await redis_cli.get(
                                name=f"{message.from_user.id}_is_active_account"  # noqa
                            )
                        )
                    )
                await state.clear()
        elif user_answ == "все районы":
            if len(DISTRICTS) > len(user_distr):
                key: str
                for key in DISTRICTS:
                    if str(DISTRICTS[key]) not in user_distr:
                        user_distr.append(str(DISTRICTS[key]))
                await message.answer(
                    text="Успешно добавил все районы в твой список"
                )
            elif len(DISTRICTS) == len(user_distr):
                user_distr = []
                await message.answer(
                    text="Все районы успешно были убраны со списка"
                )
            await redis_cli.set(
                name=distr_name,
                value=dumps(obj=user_distr),
                ex=ONE_MONTH_SECONDS
            )
        elif user_answ in DISTRICTS:
            is_already_selected: bool = str(DISTRICTS[user_answ]) in user_distr
            if is_already_selected:
                user_distr.remove(str(DISTRICTS[user_answ]))
                await message.answer(
                    text=f"Ранее выбранный вами {user_answ.capitalize()} "
                    "район успешно убран из списка выбранных районов."
                )
            elif not is_already_selected:
                user_distr.append(str(DISTRICTS[user_answ]))
                await message.answer(
                    text=f"Район {user_answ} успешно добавлен "
                    "в ваш список."
                )
            await redis_cli.set(
                name=distr_name,
                value=dumps(obj=user_distr),
                ex=ONE_MONTH_SECONDS
            )
        elif user_answ not in DISTRICTS:
            await message.answer(
                text="Извините, но данный район не представлен.\r\n"
                "Пожалуйста, выбирайте из того списка, который вам представлен"
            )

        distr_message: str = "Список пуст" \
            if len(user_distr) == 0 \
            else ", ".join([DISTRICTS_IDS[int(dist)] for dist in user_distr])
        await message.answer(
            text=f"Выбранные районы: {distr_message}\r\n"
        )

    elif not jwt_token:
        await message.answer(
            text="Извините, но вы должны для начала авторизоваться",
            reply_markup=get_main_reply_keyboard()
        )
