import logging

from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware, exceptions
from aiogram.types import TelegramObject, CallbackQuery

from bot import bot


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GettingStartedTips(BaseMiddleware):
    def __init__(self):
        self._last_msg = 0
        self._messages = {
            'back_to_decks': 'Message 1',
            'show_cards_': 'Message 2',
        }
        self._tips_count = {tip: 1 for tip in self._messages}

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:

        if isinstance(event, CallbackQuery):
            message = event.message
            trigger = event.data
        else:
            message = event
            trigger = event.text
        tip_message = await self._message_handler(trigger)
        if tip_message:
            message_id = self._last_msg
            chat_id = message.chat.id
            if self._last_msg != 0:
                try:
                    await bot.delete_message(chat_id=chat_id, message_id=message_id)
                except exceptions as e:
                    logger.error(f"Failed to delete message {message_id} in chat {chat_id}: {e}")

            msg = await message.answer(tip_message)
            self._last_msg = msg.message_id

        return await handler(event, data)

    async def _message_handler(self, trigger: str):
        for msg, tip in self._messages.items():
            if trigger.startswith(msg):
                if self._tips_count[msg] == 0:
                    return
                else:
                    self._tips_count[msg] -= 1
                    if sum(self._tips_count.values()) == 0:
                        await self._unregister_middleware()
                    return tip

    async def _unregister_middleware(self):
        from app.handlers import main_router
        main_router.message.middleware.unregister(self)
        main_router.callback_query.middleware.unregister(self)
