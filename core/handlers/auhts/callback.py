# Python
from typing import (
    Tuple,
    Any,
    Dict,
    List,
)

# Third party
from aioredis import Redis

# Aiogram
from aiogram.types import CallbackQuery
from aiogram import Bot
from aiogram.fsm.context import FSMContext

# Project
from core.utils.fsm.auths.states_auths import RegistrationSteps


async def select_registration(
    call: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Triggers when the use chose register inlint btn."""
    await call.message.answer(
        text="Ура! Ты сделал правильный выбор!\r\n"
        "Начинаем регистрацию..."
    )
    await call.message.answer(
        text="Пожалуйста, введите адрес вашей почты (email)"
    )
    call.answer()
    await state.set_state(state=RegistrationSteps.GET_EMAIL)


async def finish_district_selection(
    call: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Triggers when the user chooses finish inline btn."""
    distr_name: str = f"{call.message.from_user.id}_districts"
    districts: List[int] = await list(redis_cli.get(name=distr_name)) \
        if await redis_cli.get(name=distr_name) \
        else []
    if len(districts) == 0:
        await call.message.answer(
            text="Вам необходимо выбрать хотя бы 1 район, чтобы продолжить."
        )
    elif len(districts) > 0:
        await call.message.answer(
            text="Отлично! Отправляем запрос на "
            "получение данных по вашим параметрам."
        )
        state.update_data(districts=districts)
        context_data: Dict[str, Any] = await state.get_data()
        await call.message.answer(
            text=f"Сохранённые данные в машине состояний:\r\n"
            f"{str(context_data)}"
        )
        state.clear()
