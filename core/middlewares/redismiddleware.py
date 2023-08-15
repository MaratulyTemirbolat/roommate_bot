# Python
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Coroutine,
)

# Third party
from aiogram.types import Message
from aioredis import Redis

# Aiogram
from aiogram import BaseMiddleware


class RedisMiddleware(BaseMiddleware):
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Coroutine[Any, Any, Any]:
        data["redis_cli"] = self.redis
        return await handler(event, data)
