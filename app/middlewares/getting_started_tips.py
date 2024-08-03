import asyncio
import logging
import random
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware, exceptions
from aiogram.enums import ParseMode
from aiogram.types import TelegramObject, CallbackQuery

from app.utils import set_initial_user_language
from bot import bot
from app.middlewares.i18n_init import i18n

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_ = i18n.gettext

class GettingStartedTips(BaseMiddleware):
    def __init__(self):
        self._last_msg = 0
        self._messages = {
            'deck_details_': _('deck_details_tip'),
            'show_cards_': _('show_cards_tip'),
            'delete_card': _('delete_card_tip'),
            'add_card_': (_('add_card_tip_1'), _('add_card_tip_2')),
            'edit_card': _('edit_card_tip'),
            'import_cards_': _('import_cards_tip'),
            'choose_study_format_': _('choose_study_format_tip'),
            'start_studying_': _('start_studying_tip'),
            'button_show_back': _('button_show_back_tip'),
            'rating': (_('rating_tip_1'), _('rating_tip_2')),
            '/addcard': _('addcard_command_tip'),
        }
        self._tips_count = {tip: 1 for tip in self._messages}
        self._tips_count['rating'] = 2
        self._tips_count['add_card_'] = 2

    @property
    def last_msg(self):
        return self._last_msg

    @last_msg.setter
    def last_msg(self, msg: int):
        self._last_msg = msg

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

        event_handler = await handler(event, data)

        self.chat_id = message.chat.id
        state = data['state']
        self.telegram_id = state.key.user_id
        if trigger.startswith('back_to_decks') or trigger.startswith('deck_details_'):
            await self._delete_message()

        tip_message = await self._message_handler(trigger)
        if tip_message:
            if self._last_msg != 0:
                await self._delete_message()
            emoji = random.choice(('🚨', '💡', '☝️', '🚀', '🚩'))
            msg = await message.answer(f'{emoji} {_("tip")}\n<blockquote>{tip_message}</blockquote>', parse_mode=ParseMode.HTML)
            self._last_msg = msg.message_id

        return event_handler

    async def _message_handler(self, trigger: str):
        for trig, tip in self._messages.items():
            if trigger in ('Again', 'Hard', 'Good', 'Easy'):
                trigger = 'rating'
            if trigger.startswith(trig):
                if self._tips_count[trig] == 0:
                    return
                else:
                    if isinstance(tip, tuple):
                        tip = tip[self._tips_count[trig] - 1]
                    self._tips_count[trig] -= 1
                    print(self._tips_count)
                    if sum(self._tips_count.values()) == 0:
                        await self._unregister_middleware()
                    elif sum(self._tips_count.values()) == 4:
                        await self._pre_disable_getting_started_tips()
                    return tip

    async def _unregister_middleware(self):
        from app.handlers import main_router
        main_router.message.middleware.unregister(self)
        main_router.callback_query.middleware.unregister(self)

    async def _delete_message(self):
        try:
            await asyncio.create_task(bot.delete_message(chat_id=self.chat_id, message_id=self._last_msg))
        except Exception as e:
            logger.error(f"Failed to delete message {self._last_msg} in chat {self.chat_id}: {e}")

    async def _pre_disable_getting_started_tips(self):
        from app.middlewares.locales import i18n_middleware
        language = await i18n_middleware.get_lang()
        await set_initial_user_language(self.telegram_id, language.lower())
