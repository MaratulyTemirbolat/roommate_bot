# Project
from core.models.auths import CustomUserList
from core.utils.fsm.auths.states_search import GENDERS_SHORT


def get_valid_phone_number(mobile_phone: str) -> str:
    return "+7" + mobile_phone[1:] \
        if mobile_phone.startswith("8") else mobile_phone


def get_short_user_info(user: CustomUserList) -> str:
    """Get short user info for users list."""
    account_status: str = 'В активном поиске' \
        if user.is_active_account else "Не в поиске"
    user_districts: str = "".join(
        [f'\nрайон <b>{distr.name.capitalize()}</b> (город <b>{distr.city.name.capitalize()}</b>)' for distr in user.districts]  # noqa
    )
    return (
        f"Пользователь: <b>{user.first_name.capitalize()}</b>\r\n"
        f"Пол пользователя: {GENDERS_SHORT[user.gender].capitalize()}\r\n"
        f"Статус пользователя: {account_status}\r\n\n"
        f"Готов(а) платить ежемесячно: <b>{user.month_budjet} тенге</b>\r\n\n"
        f"Информация о пользователе: {'Отсутствует' if not user.comment else user.comment}\r\n\n"  # noqa
        f"Готов(а) жить в районах:\n{user_districts}"
    )


def get_user_contact_info(user: CustomUserList) -> str:
    """Get user's telegram info."""
    return (
        f"Телеграм пользователя {user.first_name}: @{user.telegram_username}\n"
    )


def get_user_detail_info(user: CustomUserList) -> str:
    """Get detailed user information."""
    account_status: str = 'В активном поиске людей' \
        if user.is_active_account else "Не в поиске людей"
    user_districts: str = "\n".join(
        [f'район <b>{distr.name.capitalize()}</b> (город <b>{distr.city.name.capitalize()}</b>)' for distr in user.districts]  # noqa
    ) if len(user.districts) > 0 else "Не указано"
    telegram: str = "Отсутствует" \
        if not user.telegram_username \
        else "@"+user.telegram_username
    admin_text: str = "Вы администратор" \
        if user.is_superuser \
        else "Вы не администратор"
    return (
        f"Имя: <b>{user.first_name.capitalize()}</b>\r\n"
        f"Ваша почта: {user.email}\r\n"
        f"Номер телефона: {user.phone}\r\n"
        f"Дата создания личного профиля: {user.datetime_created}\r\n"
        f"Статус администратора: {admin_text}\r\n"
        f"Имя пользователя в телеграм: {telegram}\r\n"
        f"Пол пользователя: {GENDERS_SHORT[user.gender].capitalize()}\r\n"
        f"Статус пользователя: {account_status}\r\n\n"
        f"Готов(а) платить ежемесячно: <b>{user.month_budjet} тенге</b>\r\n\n"
        f"Информация о пользователе: {'Отсутствует' if not user.comment else user.comment}\r\n\n"  # noqa
        f"Готов(а) жить в районах: {user_districts}"
    )
