# Python
from typing import (
    Any,
    Dict,
    Tuple,
    Callable,
    Optional,
)

# Third party
from aioredis import Redis

# Aiogram
from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

# Project
from core.keyboards.inline.inline import get_preregister_keyboards
from core.keyboards.reply.reply import (
    own_phone_number_keyboard,
    get_name_keyboard,
    gender_keyboard,
    GENDER_OPTIONS,
    get_main_reply_keyboard,
)
from core.utils.validators import (
    is_valid_email,
    is_convertable_str_to_int,
    is_positive_number,
    is_money_limit,
)
from core.utils.fsm.auths.states_auths import (
    RegistrationSteps,
    AuthorizationSteps,
)
from core.utils.utils import get_valid_phone_number
from core.api.services import handle_post
from core.settings import ONE_MONTH_SECONDS


async def register_handler_cmd(
    message: Message,
    bot: Bot,
    redis_cli: Redis,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle user registration."""
    # await redis_cli.set(name=message.from_user.id, value="12345", ex=100)
    is_registered: Optional[Any] = await redis_cli.get(
        name=message.from_user.id
    )
    if not is_registered:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f"<b>{message.from_user.first_name}</b>."
            "Я очень рад, что ты решил к нам присоединиться!\r\n"
            "Перед началось регистрации, прошу ознакомиться с "
            "правилами пользования приложения, "
            "нажав на соответствующую кнопку.",
            reply_markup=get_preregister_keyboards()
        )
    elif is_registered:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="Извините, но вы уже авторизованы в системе.\r\n"
            "Нет необходимости регистрироваться!"
        )


async def get_email_registration(
    message: Message,
    bot: Bot,
    state: FSMContext,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle EMAIL state in registration process."""
    provided_email: str = message.text.strip().lower()
    is_valid: bool = is_valid_email(email=provided_email)
    print(is_valid)
    if is_valid:
        await message.answer(
            text=f"Ваша почта {provided_email}\r\n"
            "Теперь предоставьте ваш номер телефона нажав на кнопку ниже",
            reply_markup=own_phone_number_keyboard
        )
        await state.update_data(email=provided_email)
        await state.set_state(state=RegistrationSteps.GET_PHONE)
    elif not is_valid:
        await message.answer(
            text="Вы ввели почту неккоректно. Пожалуйста введите еще раз."
        )


async def get_phone_registration(
    message: Message,
    bot: Bot,
    state: FSMContext,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle PHONE state in registration process."""
    valid_phone_number: str = get_valid_phone_number(
        mobile_phone=message.contact.phone_number
    )
    await message.answer(
        text=f"Контак принят! Ваш номер: {valid_phone_number}\r\n"
        "Оставить ли для других пользователей "
        f"имя: <b>{message.from_user.first_name}</b> ?\r\n"
        "Если нет, то впишите имя по которому вас будут находить другие люди",
        reply_markup=get_name_keyboard(message.from_user.first_name)
    )
    await state.update_data(phone=valid_phone_number)
    await state.set_state(state=RegistrationSteps.GET_FIRST_NAME)


async def get_fake_phone_registration(
    message: Message,
    *args: Tuple[Any],
    **kwargs: Dict[str, Any]
) -> None:
    """Handle PHONE state with fake contact."""
    await message.answer(
        text="Извините, но мне нужен ваш контакт, а не кого-то другого.\r\n"
        "Отправьте еще раз, но только свой!"
    )


async def get_first_name_registration(
    message: Message,
    bot: Bot,
    state: FSMContext,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle FIRST NAME state in registration."""
    first_name: str = (
        message.from_user.first_name
        if message.text.find("Оставить как") != -1
        else message.text.lower()
    ).capitalize()

    await message.answer(
        text=f"Превосходно! Имя, которое будет использовано: {first_name}\r\n"
        "Осталось совсем немного! Поднажмите!\r\n"
        "Пожалуйста, выберите ваш пол: ",
        reply_markup=gender_keyboard
    )
    await state.update_data(first_name=first_name)
    await state.set_state(state=RegistrationSteps.GET_GENDER)


async def get_gender_registration(
    message: Message,
    bot: Bot,
    state: FSMContext,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle GENDER state in registration."""
    if message.text.lower() in GENDER_OPTIONS:
        await message.answer(
            text=f"Вы выбрали пол: '{message.text}'\r\n"
            "Впишите ваш максимальный месячный бюджет, который вы готовы "
            "использовать, в качестве, арендной платы"
        )
        await state.update_data(gender=GENDER_OPTIONS[message.text.lower()])
        await state.set_state(state=RegistrationSteps.GET_MONTH_BUDJET)
    else:
        await message.reply(
            text="Упс! Кажется вы совершили ошибку, когда вписывали пол.\r\n"
            "Пожалуйста, повторите.",
            reply_markup=gender_keyboard
        )


async def get_month_budjet_registration(
    message: Message,
    bot: Bot,
    state: FSMContext,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle MONTH BUDJET state in registration process."""
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
        is_valid, error_msg = validator(user_budjet, "месячный бюджет")
        if not is_valid:
            await message.reply(
                text=f"{error_msg}\r\nПопробуйте еще раз, пожалуйста."
            )
            break

    if is_valid:
        await message.answer(
            text=f"Хорошо! Ваша сумма составляет: {int(user_budjet)} тенге.\n"
            "Осталось всего 2 шага (необходим пароль и "
            "комментарий для других людей) :D.\r\n"
            "Напечатайте ваш пароль: "
        )
        await state.update_data(month_budjet=int(user_budjet))
        await state.set_state(state=RegistrationSteps.GET_PASSWORD)


async def get_password_registration(
    message: Message,
    bot: Bot,
    state: FSMContext,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle PASSWORD state in registration process."""
    user_password: str = message.text.strip()
    if user_password:
        await message.answer(
            text=f"Хоп, хоп :D Теперь я знаю твой пароль '{user_password}'"
            "Извини, всего лишь шучу. Но, у нас финишная прямая, "
            "остался только комментарий, который позволите более точнее "
            "находить тебе новых людишек ^_^\r\nПожалуйста, напечатай коммент,"
            " который ты считаешь важным для себя при подборе, чтобы другие "
            "его видели"
        )
        await message.answer(
            text="Введите пожалуйста комментарий"
        )
        await state.update_data(password=user_password)
        await state.update_data(telegram_username=message.from_user.username)
        await state.set_state(state=RegistrationSteps.GET_COMMENT)
    if not user_password:
        await message.answer(
            text="Упс. Кажется, ты ввел пароль, который состоит из ничего\r\n"
            "Постарайся, я в тебя верю! Попробуй еще раз :3"
        )


async def get_comment_registration(
    message: Message,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle COMMENT state in registration process."""
    comment: str = message.text.strip()
    if comment:
        await message.answer(
            text="Ты это сделал! Молодчина! Отправляю твои данные"
            " на регистрацию. Включаем режим ждуна на пару секундн :D"
        )
        await state.update_data(comment=comment)
        context_data: Dict[str, Any] = await state.get_data()
        await message.answer(
            text=f"Сохранённые данные в машине состояний:\r\n"
            f"{str(context_data)}"
        )
        response: Dict[str, Any] = await handle_post(
            url="http://localhost:8000/api/v1/auths/users/register_user",
            data=context_data
        )

        if int(response.get("status")) >= 400:
            errors_text: str = ""
            key: str
            for key in response.get("response"):
                errors_text += response.get("response")[key][0] + "\r\n"

            await message.answer(
                text="Произошла ошибка при регистрации...\r\n"
                f"{errors_text}",
                reply_markup=get_main_reply_keyboard()
            )
        elif int(response.get("status")) >= 200 and int(response.get("status")) < 300:  # noqa
            redis_cli.set(
                name=message.from_user.id,
                value=response.get("response")["access"],
                ex=ONE_MONTH_SECONDS
            )
            await message.answer(
                text="Мои поздравления! Вы успешно зарегистрировались!",
                reply_markup=get_main_reply_keyboard(is_registered_user=True)
            )
        await state.clear()

    elif not comment:
        await message.answer(
            text="Ты ничего не ввел :_(\r\n)"
            "Пожалуйста, введите комментарий о себе."
        )


# Authorization
async def login_handle_cmd(
    message: Message,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle the beginning of the autorization process."""
    is_registered: Optional[Any] = await redis_cli.get(
        name=message.from_user.id
    )
    if not is_registered:
        await message.answer(
            text="Для того, чтобы войти в"
            "систему вам нужно ввести почту (email) "
            "или номер телефона, который привязан к вашему аккаунту.\r\n"
            "Номер телефона необходимо вводить <b>БЕЗ</b> начала кода страны."
        )
        await state.set_state(
            state=AuthorizationSteps.GET_EMAIL_PHONE_USERNAME
        )
    elif is_registered:
        await message.answer(
            text="Вы уже авторизированы! Нет необходимости делать это снова"
        )


async def get_email_phone_login(
    message: Message,
    bot: Bot,
    state: FSMContext,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle EMAIL_PHONE state autorization process."""
    input_data: str = message.text.strip().lower()
    is_email: bool = is_valid_email(input_data)
    is_number: bool = is_convertable_str_to_int(
        inp_str=input_data,
        variable_name=""
    )[0]
    if not is_email and not is_number:
        await message.answer(
            text="Вам необходимо ввести почту или номер телефона, "
            "но без кода страны, т.е. без +7 и без 8"
        )
    else:
        input_data = get_valid_phone_number(
            mobile_phone=input_data
        ) if is_number else input_data
        await message.answer(
            text=f"Вы ввели <b>'{input_data}'</b>\r\n"
            "Теперь введите пароль от вашего аккаунта"
        )
        await state.update_data(login_data=input_data)
        await state.set_state(state=AuthorizationSteps.GET_PASSWORD)


async def get_password_login(
    message: Message,
    bot: Bot,
    state: FSMContext,
    redis_cli: Redis,
    *args: Tuple[Any],
    **kwargs: Dict[Any, Any]
) -> None:
    """Handle PASSWORD state for authorization process."""
    password: str = message.text
    await message.answer(
        text="Отлично! Пароль принят. Пробую авторизоваться!"
    )
    await state.update_data(password=password)
    context_data: Dict[str, Any] = await state.get_data()
    await message.answer(
        text=f"Сохранённые данные в машине состояний:\r\n"
        f"{str(context_data)}"
    )
    response: Dict[str, Any] = await handle_post(
        url="http://localhost:8000/api/v1/auths/users/login",
        data=context_data
    )
    if int(response.get("status")) >= 400:
        await message.answer(
            text="Произошла ошибка при авторизации...\r\n"
            f"{response.get('response')['response']}",
            reply_markup=get_main_reply_keyboard()
        )
    elif int(response.get("status")) >= 200 and int(response.get("status")) < 300:  # noqa
        await redis_cli.set(
            name=message.from_user.id,
            value=response.get("response")["access"],
            ex=ONE_MONTH_SECONDS
        )
        await message.answer(
            text="Мои поздравления! Вы успешно авторизовались!",
            reply_markup=get_main_reply_keyboard(is_registered_user=True)
        )
    await state.clear()

# Осталось совсем немного! Поднажмите!\r\n"
# "Пожалуйста, выберите пол, который вы бы хотели видеть среди людей.r\n"
# "Мы будем отправлять вам людей, согласно вашим предпочтениям :3",
