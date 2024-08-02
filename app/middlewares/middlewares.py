from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        data['start_time'] = datetime.now()
        logger.info(f"\n                                   Запрос получен: {data['start_time']}")
        result = await handler(event, data)
        end_time = datetime.now()
        start_time = data.get('start_time')
        duration = (end_time - start_time).total_seconds()
        logger.info(f"\n                                   Ответ отправлен: {end_time}, Время обработки: {duration} секунд")
        return result



