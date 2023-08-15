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

# Aiogram
from aiogram.types import Message
from aiogram import Bot
from aiogram.fsm.context import FSMContext

# Project
from core.utils.validators import (
    is_convertable_str_to_int,
    is_positive_number,
    is_money_limit,
)
from core.keyboards.reply.searchkeyboards import (
    get_preferred_sex_keyboard,
    get_keyboard_by_data_sequence,
)
from core.keyboards.inline.inline import get_finish_districts_search
from core.utils.fsm.auths.states_search import (
    UsersSearchSteps,
    GENDERS,
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
    is_registered: Optional[Any] = await redis_cli.get(
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
        await message.answer(
            text=f"Хорошо! Ваша сумма составляет: {int(user_budjet)} тенге.\n"
            "Теперь, вам необходимо выбрать город, где в котором будете жить.",
            reply_markup=get_keyboard_by_data_sequence(
                data=("Алматы",),
                one_time_keyboard=True
            )
        )
        await state.update_data(month_budjet=user_budjet)
        await state.set_state(state=UsersSearchSteps.GET_PREFERED_CITY)


async def get_preferred_city(
    message: Message,
    bot: Bot,
    state: FSMContext,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle PREFERED_CITY state for searching process."""
    city: str = message.text.strip().lower()
    if city not in CITIES:
        await message.answer(
            text="Извините, но такого города нет. Повторите попытку еще раз"
        )
    elif city in CITIES:
        await state.update_data(city=CITIES.get(city))
        await state.set_state(state=UsersSearchSteps.GET_PREFERED_DISTRICTS)
        await message.answer(
            text=f"Вы выбрали город '{city.capitalize()}'. Пожалуйста,"
            " выберете районы, которые вы хотите видеть",
            reply_markup=get_keyboard_by_data_sequence(
                data=DISTRICTS_IDS.values(),
                one_time_keyboard=False
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
    distr_name: str = f"{message.from_user.id}_districts"
    districts: List[int] = await list(redis_cli.get(name=distr_name)) \
        if await redis_cli.get(name=distr_name) \
        else []
    selected_distr: str = message.text.strip().lower()
    if selected_distr in DISTRICTS:
        is_already_selected: bool = DISTRICTS[selected_distr] in districts
        if is_already_selected:
            districts.remove(DISTRICTS[selected_distr])
            await message.answer(
                text=f"Ранее выбранный вами {selected_distr.capitalize()}"
                " убран из списка выбранных районов"
            )
        elif not is_already_selected:
            districts.append(DISTRICTS[selected_distr])
            await message.answer(
                text=f"Район {selected_distr.capitalize()} успешно добавлен "
                "в собранный вами список."
            )
        await redis_cli.set(
            name=distr_name,
            value=districts,
            ex=ONE_MONTH_SECONDS
        )
    elif selected_distr == "все районы":
        if len(DISTRICTS) > len(districts):
            key: str
            for key in DISTRICTS:
                if DISTRICTS[key] not in districts:
                    districts.append(DISTRICTS[key])
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
            value=districts,
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
            f"{[DISTRICTS_IDS[distr_id] for distr_id in districts]}",
            reply_markup=get_finish_districts_search()
        )
