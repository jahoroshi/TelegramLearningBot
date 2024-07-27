from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message


class TestMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        # print('Действия до обработчика')
        # if isinstance(event, Message):
        #     print("Сообщение отправлено ботом:", event)
        result = await handler(event, data)
        # print('Действие после обработчика')
        return result


