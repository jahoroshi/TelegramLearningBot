import asyncio
import logging
import random
from typing import Dict, Any, Tuple

from aiogram.enums import ParseMode
from aiogram.types import TelegramObject

from app.exceptions import DisableTipModeForUser
from app.middlewares.i18n_init import i18n
from app.utils import set_initial_user_language
from bot import bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GettingStartedTips:
    def __init__(self):
        self.last_message: Dict[int, int] = {}
        self.messages: Dict[str, Dict[str, str]] | None = None
        self.tips_count: Dict[int, Dict[str, int]] = {}
        self.allowed_triggers: Tuple[str, ...] = ('back_to', 'Again', 'Hard', 'Good', 'Easy')

    @property
    def last_msg(self):
        return self.last_message

    @last_msg.setter
    def last_msg(self, data: Tuple[int, int]):
        msg, user_id = data
        self.last_message[user_id] = msg

    async def process_tip_message(self,
                                  event: TelegramObject,
                                  data: Dict[str, Any],
                                  locale: str) -> Any:

        if event.callback_query:
            message = event.callback_query.message
            trigger = event.callback_query.data
        else:
            message = event.message
            trigger = event.message.text

        if self.messages is None:
            await self._init_messages()

        trigger = "_".join(trigger.split('_')[:2])
        if trigger not in self.messages['en'] and trigger not in self.allowed_triggers:
            return

        chat_id = message.chat.id
        state = data['state']
        user_id = state.key.user_id

        if last_message := self.last_message.get(user_id):
            await self._delete_message(chat_id, last_message, user_id)

        tip_message = await self._message_handler(trigger, user_id, locale)
        if tip_message:
            emoji = random.choice(('🚨', '🌟', '☝️', '🚀', '🚩', '👋'))
            msg = await message.answer(f'{emoji} {i18n.gettext("tip")}\n<blockquote>{tip_message}</blockquote>',
                                       parse_mode=ParseMode.HTML)
            self.last_message[user_id] = msg.message_id
        return


    async def _message_handler(self, trigger: str, user_id: int, locale: str):
        messages = self.messages.get(locale, {})

        if trigger in self.allowed_triggers[1:]:
            trigger = 'rating'

        if tip := messages.get(trigger):
            user_tip_counter = await self.get_user_tip_counter(user_id)
            if user_tip_counter[trigger] == 0:
                self.tips_count[user_id] = user_tip_counter
                return
            else:
                if isinstance(tip, tuple):
                    tip = tip[user_tip_counter[trigger] - 1]
                user_tip_counter[trigger] -= 1
                print(user_tip_counter)
                if sum(user_tip_counter.values()) == 4:
                    await self.pre_disable_getting_started_tips(user_id, locale)
                elif sum(user_tip_counter.values()) == 0:
                    await self.pre_disable_getting_started_tips(user_id, locale)
                    raise DisableTipModeForUser(user_id)
                self.tips_count[user_id] = user_tip_counter
                return tip


    async def _delete_message(self, chat_id, last_msg, user_id):
        if last_msg:
            try:
                await asyncio.create_task(bot.delete_message(chat_id=chat_id, message_id=last_msg))
            except Exception as e:
                logger.error(f"                   Failed to delete message {last_msg} in chat {chat_id}: {e}")
            finally:
                del self.last_message[user_id]

    async def pre_disable_getting_started_tips(self, user_id: int, locale: str):
        await set_initial_user_language(user_id, locale.lower())

    async def _init_messages(self):
        base_messages = {
            'deck_details': 'deck_details_tip',
            'show_cards': 'show_cards_tip',
            'delete_card': 'delete_card_tip',
            'add_card': ('add_card_tip_1', 'add_card_tip_2'),
            'edit_card': 'edit_card_tip',
            'import_cards': 'import_cards_tip',
            'choose_study': 'choose_study_format_tip',
            'start_studying': 'start_studying_tip',
            'button_show': 'button_show_back_tip',
            'rating': ('rating_tip_1', 'rating_tip_2'),
            '/addcard': 'addcard_command_tip',
        }

        self.messages = {
            locale: {
                key: (
                    tuple(i18n.gettext(v, locale=locale) for v in value)
                    if isinstance(value, tuple) else i18n.gettext(value, locale=locale)
                )
                for key, value in base_messages.items()
            }
            for locale in ('en', 'ru')
        }

        special_tips = {
            'rating': 2,
            'add_card': 2,
        }
        self._base_tips_count = {tip: special_tips.get(tip, 1) for tip in base_messages}

    async def get_user_tip_counter(self, user_id: int):
        tip_counter = self.tips_count.get(user_id)
        if tip_counter:
            return tip_counter
        else:
            return self._base_tips_count.copy()

#
# import asyncio
# import logging
# import random
# from typing import Callable, Dict, Any, Awaitable
#
# from aiogram import BaseMiddleware
# from aiogram.enums import ParseMode
# from aiogram.types import TelegramObject, CallbackQuery
#
# from app.middlewares.i18n_init import i18n
# from app.utils import set_initial_user_language
# from bot import bot
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# _ = i18n.gettext
#
#
# class GettingStartedTips(BaseMiddleware):
#     def __init__(self):
#         self._last_msg = 0
#         self._messages = None
#         self._tips_count = None
#
#     @property
#     def last_msg(self):
#         return self._last_msg
#
#     @last_msg.setter
#     def last_msg(self, msg: int):
#         self._last_msg = msg
#
#     async def __call__(self,
#                        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
#                        event: TelegramObject,
#                        data: Dict[str, Any]) -> Any:
#
#         if isinstance(event, CallbackQuery):
#             message = event.message
#             trigger = event.data
#         else:
#             message = event
#             trigger = event.text
#
#         if self._messages is None:
#             await self._init_messages()
#
#         event_handler = await handler(event, data)
#
#         self.chat_id = message.chat.id
#         state = data['state']
#         self.telegram_id = state.key.user_id
#         if trigger.startswith('back_to_decks') or trigger.startswith('deck_details_'):
#             await self._delete_message()
#
#         tip_message = await self._message_handler(trigger)
#         if tip_message:
#             if self._last_msg != 0:
#                 await self._delete_message()
#             emoji = random.choice(('🚨', '💡', '☝️', '🚀', '🚩'))
#             msg = await message.answer(f'{emoji} {_("tip")}\n<blockquote>{tip_message}</blockquote>',
#                                        parse_mode=ParseMode.HTML)
#             self._last_msg = msg.message_id
#         print('///---', event.from_user.id, '.....', self._last_msg, '.......', self._tips_count)
#         return event_handler
#
#     async def _message_handler(self, trigger: str):
#         for trig, tip in self._messages.items():
#             if trigger in ('Again', 'Hard', 'Good', 'Easy'):
#                 trigger = 'rating'
#             if trigger.startswith(trig):
#                 if self._tips_count[trig] == 0:
#                     return
#                 else:
#                     if isinstance(tip, tuple):
#                         tip = tip[self._tips_count[trig] - 1]
#                     self._tips_count[trig] -= 1
#                     print(self._tips_count)
#                     if sum(self._tips_count.values()) == 0:
#                         await self._unregister_middleware()
#                     elif sum(self._tips_count.values()) == 4:
#                         await self._pre_disable_getting_started_tips()
#                     return tip
#
#     async def _unregister_middleware(self):
#         from app.handlers import main_router
#         main_router.message.middleware.unregister(self)
#         main_router.callback_query.middleware.unregister(self)
#
#     async def _delete_message(self):
#         try:
#             await asyncio.create_task(bot.delete_message(chat_id=self.chat_id, message_id=self._last_msg))
#         except Exception as e:
#             logger.error(f"Failed to delete message {self._last_msg} in chat {self.chat_id}: {e}")
#
#     async def _pre_disable_getting_started_tips(self):
#         from app.middlewares.locales import i18n_middleware
#         language = await i18n_middleware.get_lang()
#         await set_initial_user_language(self.telegram_id, language.lower())
#
#     async def _init_messages(self):
#         self._messages = {
#             'deck_details_': _('deck_details_tip'),
#             'show_cards_': _('show_cards_tip'),
#             'delete_card': _('delete_card_tip'),
#             'add_card_': (_('add_card_tip_1'), _('add_card_tip_2')),
#             'edit_card': _('edit_card_tip'),
#             'import_cards_': _('import_cards_tip'),
#             'choose_study_format_': _('choose_study_format_tip'),
#             'start_studying_': _('start_studying_tip'),
#             'button_show_back': _('button_show_back_tip'),
#             'rating': (_('rating_tip_1'), _('rating_tip_2')),
#             '/addcard': _('addcard_command_tip'),
#         }
#         self._tips_count = {tip: 1 for tip in self._messages}
#         self._tips_count['rating'] = 2
#         self._tips_count['add_card_'] = 2
