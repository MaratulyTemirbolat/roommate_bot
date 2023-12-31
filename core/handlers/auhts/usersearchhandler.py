# Python
from typing import (
    Tuple,
    Any,
    Dict,
    Optional,
    Callable,
    List,
)

# Third party
from aioredis import Redis
from pickle import loads

# Aiogram
from aiogram.types import Message
from aiogram import Bot
from aiogram.fsm.context import FSMContext

# Project
from core.keyboards.reply.reply import get_main_reply_keyboard
from core.utils.validators import (
    is_convertable_str_to_int,
    is_positive_number,
    is_money_limit,
)
from core.keyboards.reply.searchkeyboards import get_preferred_sex_keyboard
from core.keyboards.inline.inline import get_finish_districts_search
from core.utils.fsm.auths.states_search import (
    UsersSearchSteps,
    GENDERS,
    GENDERS_SHORT,
    CITIES,
    DISTRICTS,
    DISTRICTS_IDS,
)
from core.settings import ONE_MONTH_SECONDS


async def handle_search_cmd(
    message: Message,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle searching users by parameters."""
    await state.clear()
    is_registered: Optional[bytes] = await redis_cli.get(
        name=message.from_user.id
    )
    if not is_registered:
        await message.answer(
            text="Извините, но вы не авторизированы, чтобы выполнять "
            "поиск других людей.\r\nСначала авторизуйтесь  "
            "или зарегистрируйтесь в системе."
        )
    elif is_registered:
        await message.answer(
            text="Для того, чтобы начать, для начала, выберете пол, который "
            "вы хотели бы видеть.",
            reply_markup=get_preferred_sex_keyboard()
        )
        await state.set_state(state=UsersSearchSteps.GET_PREFERED_GENDER)


async def get_preferred_gender(
    message: Message,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle PREFERRED_GENDER state for processing."""
    preferred_gender: str = message.text.strip().lower()
    if preferred_gender not in GENDERS and preferred_gender != "не важно":
        await message.reply(
            text="Вам нужно выбрать между: 'Мужской', 'Женский' или 'Не важно'"
            "\nПопробуйте, пожалуйста, снова. "
        )
    elif preferred_gender in GENDERS:
        await state.update_data(gender=GENDERS.get(preferred_gender))
        await state.set_state(state=UsersSearchSteps.GET_PREFERED_MAX_BUDJET)
        await redis_cli.set(
            name=f"{message.from_user.id}_search_gender",
            value=GENDERS.get(preferred_gender)
        )
        await message.reply(
            text="Отлично, будем показывать вам людей "
            f"согласно полу '{preferred_gender.capitalize()}'\r\n"
            "Пожалуйста, теперь напишите максимальный ежемесячный платеж "
            "с которым вы хотите видеть людей."
        )
    elif preferred_gender == "не важно":
        await state.set_state(state=UsersSearchSteps.GET_PREFERED_MAX_BUDJET)
        await message.reply(
            text="Хорошо! Будем искать людей всех половых принадлежностей.\r\n"
            "Пожалуйста, теперь напишите максимальный ежемесячный платеж "
            "с которым вы хотите видеть людей."
        )


async def get_preferred_max_budjet(
    message: Message,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle PREFERRED_MAX_BUDJET state of people searching."""
    user_budjet: str = message.text
    is_valid: bool = True
    error_msg: str = ""
    budjet_validators: Tuple[Callable[[str, str], Tuple[bool, str]]] = (
        is_convertable_str_to_int,
        is_positive_number,
        is_money_limit,
    )
    validator: Callable[[str, str], Tuple[bool, str]]
    for validator in budjet_validators:
        is_valid, error_msg = validator(
            user_budjet,
            "месячный бюджет"
        )
        if not is_valid:
            await message.reply(
                text=f"{error_msg}\r\nПопробуйте еще раз, пожалуйста."
            )
            break
    if is_valid:
        city: str = "алматы"
        await state.update_data(city=CITIES.get(city))
        await message.answer(
            text=f"Хорошо! Ваша сумма составляет: {int(user_budjet)} тенге.\n",
            # "Теперь, вам необходимо выбрать город, в котором будете жить.",
            # reply_markup=get_keyboard_by_data_sequence(
            #     data=("Алматы",),
            #     one_time_keyboard=True
            # )
        )
        await message.answer(
            text=f"Выбранный город '{city.capitalize()}'.\r\n"
            "Давайте, теперь покажу вам ваши параметры для поиска :)",
            # reply_markup=get_keyboard_by_data_sequence(
            #     data=DISTRICTS_IDS.values(),
            #     extra_sequence=("все районы",),
            #     one_time_keyboard=False
            # )
        )
        await redis_cli.set(
            name=f"{message.from_user.id}_search_mongth_budjet",
            value=int(user_budjet)
        )
        await state.update_data(month_budjet=user_budjet)
        await state.set_state(state=UsersSearchSteps.GET_PREFERED_DISTRICTS)
        await get_search_districts(
            message=message,
            bot=bot,
            state=state,
            redis_cli=redis_cli,
            *args,
            **kwargs
        )


async def get_preferred_city(
    message: Message,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle PREFERED_CITY state for searching process."""
    # city: str = message.text.strip().lower()
    city: str = "алматы"
    if city not in CITIES:
        await message.answer(
            text="Извините, но такого города нет. Повторите попытку еще раз"
        )
    elif city in CITIES:
        await state.update_data(city=CITIES.get(city))
        await redis_cli.set(
            name=f"{message.from_user.id}_search_city",
            value=CITIES.get(city)
        )
        await state.set_state(state=UsersSearchSteps.GET_PREFERED_DISTRICTS)
        await redis_cli.delete(f"{message.from_user.id}_search_districts")
        await message.answer(
            text=f"Выбранный город '{city.capitalize()}'.\r\n"
            "Давайте, теперь покажу вам ваши параметры для поиска :)",
            # reply_markup=get_keyboard_by_data_sequence(
            #     data=DISTRICTS_IDS.values(),
            #     extra_sequence=("все районы",),
            #     one_time_keyboard=False
            # )
        )
        await get_search_districts(
            message=message,
            bot=bot,
            state=state,
            redis_cli=redis_cli,
            *args,
            **kwargs
        )


async def get_search_districts(
    message: Message,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle Districts during registration process."""
    distr_name: str = f"{message.from_user.id}_reg_districts"
    opt_distr: Optional[bytes] = await redis_cli.get(
        name=distr_name
    )
    user_districts: List[str] = loads(opt_distr) if opt_distr else []
    if len(user_districts) > 0:
        await state.update_data(districts=",".join(user_districts))
        context_data: Dict[str, Any] = await state.get_data()
        gender: str = context_data.get("gender", "")
        districts_names: str = ", ".join(
            [f"{DISTRICTS_IDS[int(dist)]} район" for dist in user_districts]
        )
        gender = "Не важно (парни и девушки)" \
            if not gender else GENDERS_SHORT[gender]
        await message.answer(
            text="Ваши параметры для поиска людей: \n\n"
                 f"\tПол человека: <b>{gender}</b>\n"
                 "\tМесячный бюджет: "
                 f"<b>{context_data['month_budjet']} тенге</b>\n"
                 "\tГород: <b>Алматы</b>\n\n"
                 f"\tПредпочитаемые районы: {districts_names}",
            reply_markup=get_finish_districts_search()
        )
    else:
        await message.answer(
            text="Вам необходимо выбрать хотя бы 1 район, "
            "чтобы продолжить поиск.",
            reply_markup=get_main_reply_keyboard(
                is_registered_user=await redis_cli.get(
                    name=f"{message.from_user.id}"
                ),
                is_active_account=await redis_cli.get(
                    name=f"{message.from_user.id}_is_active_account"
                )
            )
        )


async def get_preferred_districts(
    message: Message,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle PREFERRED_DISTRICTS state for searching process."""
    distr_name: str = f"{message.from_user.id}_search_districts"
    opt_distr: Optional[bytes] = await redis_cli.get(name=distr_name)
    districts: List[str] = opt_distr.decode().split(",") \
        if await redis_cli.get(name=distr_name) \
        else []
    selected_distr: str = message.text.strip().lower()
    if selected_distr in DISTRICTS:
        is_already_selected: bool = str(DISTRICTS[selected_distr]) in districts
        if is_already_selected:
            districts.remove(str(DISTRICTS[selected_distr]))
            await message.answer(
                text=f"Ранее выбранный вами {selected_distr.capitalize()}"
                " убран из списка выбранных районов"
            )
        elif not is_already_selected:
            districts.append(str(DISTRICTS[selected_distr]))
            await message.answer(
                text=f"Район {selected_distr.capitalize()} успешно добавлен "
                "в собранный вами список."
            )
        await redis_cli.set(
            name=distr_name,
            value=",".join(districts),
            ex=ONE_MONTH_SECONDS
        )
    elif selected_distr == "все районы":
        if len(DISTRICTS) > len(districts):
            key: str
            for key in DISTRICTS:
                if str(DISTRICTS[key]) not in districts:
                    districts.append(str(DISTRICTS[key]))
            await message.answer(
                text="Успешно добавил все районы в твой список."
            )
        elif len(DISTRICTS) == len(districts):
            districts = []
            await message.answer(
                text="Все районы успешно были убраны с твого списка"
            )
        await redis_cli.set(
            name=distr_name,
            value=",".join(districts),
            ex=ONE_MONTH_SECONDS
        )
    elif selected_distr not in DISTRICTS:
        await message.answer(
            text="Извините, но данный район не предоставлен.\r\n"
            "Пожалуйста, выбирайте из того списка, который вам представлен"
        )
    if len(districts) == 0:
        await message.answer(
            text="Список выбранных вами районов пуст"
        )
    elif len(districts) != 0:
        await message.answer(
            text="Списко выбранных вами районов: "
            f"{', '.join([DISTRICTS_IDS[int(distr_id)] for distr_id in districts])}",  # noqa
            reply_markup=get_finish_districts_search()
        )
