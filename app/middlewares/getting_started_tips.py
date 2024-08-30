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
    """
    Class responsible for managing and delivering getting started tips to the users based on their actions.
    """

    def __init__(self):
        """
        Initializes the GettingStartedTips with default settings.
        """
        self.last_message: Dict[int, int] = {}  # Stores the last sent tip message IDs for each user
        self.messages: Dict[str, Dict[str, str]] | None = None  # Stores the localized tip messages
        self.tips_count: Dict[int, Dict[str, int]] = {}  # Tracks the remaining tips to be sent to each user
        self.allowed_triggers: Tuple[str, ...] = (
        'back_to', 'Again', 'Hard', 'Good', 'Easy')  # Triggers that initiate tips

    @property
    def last_msg(self):
        """Getter for last_message attribute."""
        return self.last_message

    @last_msg.setter
    def last_msg(self, data: Tuple[int, int]):
        """Setter for last_message attribute."""
        msg, user_id = data
        self.last_message[user_id] = msg

    async def process_tip_message(self,
                                  event: TelegramObject,
                                  data: Dict[str, Any],
                                  locale: str) -> Any:
        """
        Processes the incoming event to determine if a tip should be sent to the user.

        Args:
            event: The Telegram event (e.g., message or callback query).
            data: Additional data passed to the middleware.
            locale: The locale of the user.
        """
        if event.callback_query:
            message = event.callback_query.message
            trigger = event.callback_query.data
        else:
            message = event.message
            trigger = event.message.text

        if self.messages is None:
            await self._init_messages()

        if trigger == 'button_show_hint':
            return

        # Normalize trigger to the first two segments, if applicable
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
        """
        Handles the retrieval of the appropriate tip message based on the trigger and user state.

        Args:
            trigger: The trigger word indicating the user's action.
            user_id: The Telegram ID of the user.
            locale: The user's locale.

        Returns:
            str: The localized tip message to be sent.
        """
        messages = self.messages.get(locale, {})

        if trigger in self.allowed_triggers[1:]:  # Normalize triggers related to ratings
            trigger = 'rating'

        if tip := messages.get(trigger):
            user_tip_counter = await self.get_user_tip_counter(user_id)
            if user_tip_counter[trigger] == 0:
                self.tips_count[user_id] = user_tip_counter
                return
            else:
                if isinstance(tip, tuple):  # Handle multi-part tips
                    tip = tip[user_tip_counter[trigger] - 1]
                user_tip_counter[trigger] -= 1
                print(user_tip_counter)
                if sum(user_tip_counter.values()) == 4:  # Specific condition to handle disabling tips
                    await self.pre_disable_getting_started_tips(user_id, locale)
                elif sum(user_tip_counter.values()) == 0:  # Disable tips when no more tips are available
                    await self.pre_disable_getting_started_tips(user_id, locale)
                    raise DisableTipModeForUser(user_id)
                self.tips_count[user_id] = user_tip_counter
                return tip

    async def _delete_message(self, chat_id, last_msg, user_id):
        """
        Deletes the last tip message sent to the user.

        Args:
            chat_id: The chat ID where the message was sent.
            last_msg: The ID of the last message to be deleted.
            user_id: The Telegram ID of the user.
        """
        if last_msg:
            try:
                await asyncio.create_task(bot.delete_message(chat_id=chat_id, message_id=last_msg))
            except Exception as e:
                logger.error(f"Failed to delete message {last_msg} in chat {chat_id}: {e}")
            finally:
                del self.last_message[user_id]

    async def pre_disable_getting_started_tips(self, user_id: int, locale: str):
        """
        Prepares the user's settings for disabling the getting started tips.

        Args:
            user_id: The Telegram ID of the user.
            locale: The user's locale.
        """
        await set_initial_user_language(user_id, locale.lower())

    async def _init_messages(self):
        """
        Initializes the localized messages for each supported locale.
        """
        base_messages = {
            'deck_details': 'deck_details_tip',
            'show_cards': 'show_cards_tip',
            'delete_card': 'delete_card_tip',
            'add_card': ('add_card_tip_1', 'add_card_tip_2'),
            'edit_card': 'edit_card_tip',
            'import_cards': 'import_cards_tip',
            'choose_study': 'choose_study_format_tip',
            'start_studying': 'start_studying_tip',
            'button_show': ('button_show_back_tip_2', 'button_show_back_tip_1'),
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
            'button_show': 2,
        }
        self._base_tips_count = {tip: special_tips.get(tip, 1) for tip in base_messages}

    async def get_user_tip_counter(self, user_id: int):
        """
        Retrieves the tip counter for the specified user, initializing it if necessary.

        Returns:
            Dict[str, int]: The tip counter for the user.
        """
        tip_counter = self.tips_count.get(user_id)
        if tip_counter:
            return tip_counter
        else:
            return self._base_tips_count.copy()
