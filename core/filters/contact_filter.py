# Python
from typing import (
    Tuple,
    Dict,
    Any,
)

# aiogram
from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsOwnerContact(BaseFilter):
    async def __call__(
        self,
        message: Message,
        *args: Tuple[Any],
        **kwargs: Dict[Any, Any]
    ) -> bool:
        """Filter whether the contact is Onwer's or not."""
        return True \
            if message.contact.user_id == message.from_user.id \
            else False
