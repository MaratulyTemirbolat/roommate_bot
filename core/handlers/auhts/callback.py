# Python
from typing import (
    Tuple,
    Any,
    Dict,
    List,
    Optional,
)
from pickle import (
    dumps,
    loads,
)

# Third party
from aioredis import Redis

# Aiogram
from aiogram.types import (
    CallbackQuery,
    URLInputFile,
)
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender

# Project
from core.utils.fsm.auths.states_auths import RegistrationSteps
from core.api.services import handle_get
from core.keyboards.reply.reply import (
    get_main_reply_keyboard,
    no_photo_keyboard,
)
from core.keyboards.inline.inline import get_next_detail_user_keyboard
from core.keyboards.reply.searchkeyboards import get_keyboard_by_data_sequence
from core.settings import ONE_MONTH_SECONDS
from core.models.auths import CustomUserList
from core.utils.utils import (
    get_short_user_info,
    get_user_contact_info,
)
from core.utils.fsm.auths.states_search import (
    UsersSearchSteps,
    DISTRICTS_IDS,
)
from core.utils.fsm.auths.account_states import PersonalAccountSteps


async def select_registration(
    call: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Triggers when the use chose register inlint btn."""
    await call.message.answer(
        text="Ура! Ты сделал(а) правильный выбор!\r\n"
        "Начинаем регистрацию..."
    )
    await call.message.answer(
        text="Пожалуйста, введите адрес вашей почты (email)"
    )
    await call.answer()
    await state.set_state(state=RegistrationSteps.GET_EMAIL)


async def hanle_user_photo(
    call: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    user: CustomUserList,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle user photo."""
    async with ChatActionSender.upload_photo(
        chat_id=call.message.chat.id,
        bot=bot
    ):
        img_url: str = user.photo \
            if user.photo \
            else "https://icon-library.com/images/no-picture-available-icon/no-picture-available-icon-20.jpg"  # noqa

        img: URLInputFile = URLInputFile(
            url=img_url,
            filename="user-logo.png"
        )
        await bot.send_photo(
            chat_id=call.message.chat.id,
            photo=img,
            caption=get_short_user_info(user=user),
            reply_markup=get_next_detail_user_keyboard()
        )
        await state.set_state(
            state=UsersSearchSteps.GET_CHOOSING_USERS_CARD
        )


async def finish_district_selection(
    call: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Triggers when the user chooses finish inline btn."""
    await call.message.answer(
        text="Отлично! Отправляем запрос на "
        "получение данных по вашим параметрам."
    )
    context_data: Dict[str, Any] = await state.get_data()

    await call.message.answer(
        text="Получаем данные по вашим критериям..."
    )

    jwt_token: Optional[bytes] = await redis_cli.get(
        name=call.message.chat.id
    )
    response: Dict[str, Any] = await handle_get(
        url="http://localhost:8000/api/v1/auths/users",
        headers={
            "Authorization": f"JWT {jwt_token.decode()}"
        },
        params=context_data
    )
    if int(response.get("status")) >= 400:
        await call.message.answer(
            text=f"Произошла ошибка. {response.get('response')}",
            reply_markup=get_main_reply_keyboard(
                is_registered_user=jwt_token,
                is_active_account=await redis_cli.get(
                    name=f"{call.message.chat.id}_is_active_account"
                )
            )
        )
    elif int(response.get("status")) >= 200 and int(response.get("status")) < 300:  # noqa
        await call.answer()
        users_quantity: int = len(response["response"]["data"])
        if users_quantity == 0:
            await call.message.answer(
                text="По вашим требованиям пользователей не было найдено",
                reply_markup=get_main_reply_keyboard(
                    is_registered_user=jwt_token,
                    is_active_account=await redis_cli.get(
                        name=f"{call.message.chat.id}_is_active_account"  # noqa
                    )
                )
            )
        elif users_quantity > 0:
            await redis_cli.set(
                name=f"{call.message.chat.id}_users_index",
                value=0,
                ex=int(ONE_MONTH_SECONDS/4)
            )
            await redis_cli.set(
                name=f"{call.message.chat.id}_pagination_users",
                value=dumps(obj=response.get("response")),
                ex=int(ONE_MONTH_SECONDS/4)
            )
            first_user: CustomUserList = CustomUserList(
                **response["response"]["data"][0]
            )
            await hanle_user_photo(
                call=call,
                bot=bot,
                state=state,
                redis_cli=redis_cli,
                user=first_user,
                *args,
                **kwargs
            )


async def users_selection(
    call: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle user choices."""
    cur_ind: Optional[int] = int(
        await redis_cli.get(name=f"{call.message.chat.id}_users_index")
    )
    user_pagination: Optional[Dict[str, Any]] = loads(
        await redis_cli.get(
            name=f"{call.message.chat.id}_pagination_users"
        )
    )
    if not user_pagination:
        await call.message.answer(
            text="Извините, но для актуальности данных "
            "необходимо повторить процедуру поиска",
            reply_markup=get_main_reply_keyboard(
                is_registered_user=True,
                is_active_account=await redis_cli.get(
                    name=f"{call.message.chat.id}_is_active_account"
                )
            )
        )
    else:
        jwt_token: Optional[bytes] = await redis_cli.get(
            name=call.message.chat.id
        )
        if call.data == "view_user_detail_btn":
            user: CustomUserList = CustomUserList(
                **user_pagination["data"][cur_ind]
            )
            await call.message.answer(
                text=get_user_contact_info(user=user),
                reply_markup=get_next_detail_user_keyboard()
            )
        elif call.data == "view_user_next_btn":
            users_quanity: int = len(user_pagination["data"])
            next_pagination_link: Optional[str] = \
                user_pagination["pagination"]["next"]
            if cur_ind + 1 < users_quanity:
                await redis_cli.set(
                    name=f"{call.message.chat.id}_users_index",
                    value=int(cur_ind+1),
                    ex=ONE_MONTH_SECONDS
                )
                next_user: CustomUserList = CustomUserList(
                    **user_pagination["data"][cur_ind+1]
                )
                await hanle_user_photo(
                    call=call,
                    bot=bot,
                    state=state,
                    redis_cli=redis_cli,
                    user=next_user,
                    *args,
                    **kwargs
                )
            elif cur_ind + 1 == users_quanity and not next_pagination_link:
                await call.message.answer(
                    text="Извините, но список пользователей по вашим "
                    "параметрам закончился.\r\n"
                    "Пожалуйста, выберите одну из опций.",
                    reply_markup=get_main_reply_keyboard(
                        is_registered_user=jwt_token,
                        is_active_account=await redis_cli.get(
                            name=f"{call.message.chat.id}_is_active_account"
                        )
                    )
                )
                await state.clear()
            elif cur_ind + 1 == users_quanity and next_pagination_link:
                response: Dict[str, Any] = await handle_get(
                    url=next_pagination_link,
                    headers={
                        "Authorization": f"JWT {jwt_token.decode()}"
                    },
                )
                await redis_cli.set(
                    name=f"{call.message.chat.id}_users_index",
                    value=0,
                    ex=int(ONE_MONTH_SECONDS/4)
                )
                await redis_cli.set(
                    name=f"{call.message.chat.id}_pagination_users",
                    value=dumps(obj=response.get("response")),
                    ex=int(ONE_MONTH_SECONDS/4)
                )
                first_user: CustomUserList = CustomUserList(
                    **response["response"]["data"][0]
                )
                await hanle_user_photo(
                    call=call,
                    bot=bot,
                    state=state,
                    redis_cli=redis_cli,
                    user=first_user,
                    *args,
                    **kwargs
                )
        elif call.data == "view_user_finish_btn":
            await call.message.answer(
                text="Подбор людей окончен по вашей инициативе.\r\n"
                "Пожалуйста, выберите одну из возможных опций.",
                reply_markup=get_main_reply_keyboard(
                    is_registered_user=jwt_token,
                    is_active_account=await redis_cli.get(
                        name=f"{call.message.chat.id}_is_active_account"
                    )
                )
            )
            await state.clear()
    await call.answer()


async def finish_distr_registration(
    call: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle Finish registration callback btn."""
    if call.data == "registration_confirm_distr_btn":
        distr_name: str = f"{call.message.chat.id}_reg_districts"
        opt_distr: Optional[bytes] = await redis_cli.get(name=distr_name)
        districts: List[str] = loads(opt_distr) if opt_distr else []
        if len(districts) > 0:
            await call.message.answer(
                text="Сохраняю выбранные вами районы...",
            )
            await state.update_data(districts=",".join(districts))
            await state.set_state(state=RegistrationSteps.GET_PHOTO)
            await call.message.answer(
                text="Теперь нужно загрузить фотографию профиля, чтобы "
                "другие люди могли видеть с кем бы они могли жить.\r\n"
                "Этот пункт необязателен, однако лучше видеть лица "
                "потенциальных соседей :)\r\n"
                "Пожалуйста, загрузите фотографию или выберите пункт 'Без фото'",  # noqa
                reply_markup=no_photo_keyboard
            )
        elif len(districts) == 0:
            await call.message.answer(
                text="Вам необходимо выбрать хотя бы 1 район, чтобы продолжить"
            )
        await call.answer()


async def prehandle_change_user_districts_btn(
    call: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Pre process handle for user's districts change."""
    await state.clear()
    jwt_token: Optional[bytes] = await redis_cli.get(
        name=f"{call.message.chat.id}"
    )
    if jwt_token:
        distr_name: str = f"{call.message.chat.id}_reg_districts"
        opt_distr: Optional[bytes] = await redis_cli.get(
            name=distr_name
        )
        user_distr: List[str] = loads(opt_distr) if opt_distr else []
        distr_message: str = "Список пуст" \
            if len(user_distr) == 0 \
            else ", ".join([DISTRICTS_IDS[int(dist)] for dist in user_distr])
        await state.set_state(
            state=PersonalAccountSteps.CHANGE_DISTRICTS_STATE
        )
        await call.message.answer(
            text=f"Вот список ваших текущих районов: {distr_message}\r\n"
            "Выберите предложенные районы: ",
            reply_markup=get_keyboard_by_data_sequence(
                data=DISTRICTS_IDS.values(),
                extra_sequence=["все районы", "отмена", "сохранить список"]
            )
        )
    elif not jwt_token:
        await call.message.answer(
            text="Извините, но вы должны для начала авторизоваться",
            reply_markup=get_main_reply_keyboard()
        )
    await call.answer()
