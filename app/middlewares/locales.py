import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, Awaitable

from aiogram.types import CallbackQuery, TelegramObject, User
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware

from app.exceptions import StopLocaleMiddlewareProcessing, DisableTipModeForUser
from app.middlewares.getting_started_tips import GettingStartedTips
from app.middlewares.i18n_init import i18n
from app.states import StartChooseLanguage
from app.utils import get_or_create_user
from bot import dp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocaleMiddleware(SimpleI18nMiddleware):
    """
    Middleware that manages localization for users based on their language preferences.
    Handles the initialization and setting of user languages and manages the locale mappings.
    """

    def __init__(
            self,
            i18n: I18n,
            tip_mode: GettingStartedTips,
            i18n_key: Optional[str] = "i18n",
            middleware_key: str = "i18n_middleware",
    ) -> None:
        """
        Initialize the LocaleMiddleware with required parameters.

        Args:
            i18n (I18n): The internationalization manager.
            tip_mode (GettingStartedTips): Middleware to handle user tips for getting started.
            i18n_key (Optional[str]): The key for accessing i18n in the middleware.
            middleware_key (str): The key for accessing this middleware instance.
        """
        super().__init__(i18n=i18n, i18n_key=i18n_key, middleware_key=middleware_key)
        self.locale_mappings: Dict[int, str] = {}  # Dictionary to store user locale mappings
        self.tip_mode = tip_mode  # Instance for handling tips
        self.next_cleanup_date = datetime.now() + timedelta(days=30)  # Schedule for memory cleanup

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        """
        Main method that processes incoming events, determines the locale, and handles tip mode if necessary.
        """
        try:
            current_locale = await self.get_locale(event=event, data=data) or self.i18n.default_locale
        except StopLocaleMiddlewareProcessing:
            return

        if self.i18n_key:
            data[self.i18n_key] = self.i18n
        if self.middleware_key:
            data[self.middleware_key] = self

        with self.i18n.context(), self.i18n.use_locale(current_locale.lower()):
            event_handler = await handler(event, data)

        if current_locale.isupper():  # Check if the locale is in uppercase (indicates a new user)
            try:
                await self.tip_mode.process_tip_message(event, data,
                                                        current_locale.lower())  # Process getting started tip
            except DisableTipModeForUser as e:
                await self.set_locale(e.user_id, current_locale.lower())  # Set locale to lowercase after tip processing

        return event_handler

    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        """
        Determines the locale for the current user based on event data and stored mappings.
        """
        event_from_user: Optional[User] = data.get("event_from_user", None)
        telegram_id = event_from_user.id
        locale = self.locale_mappings.get(telegram_id)

        if locale:
            return locale  # Return stored locale if available

        telegram_username = event_from_user.username
        user = await get_or_create_user(telegram_id, telegram_username)

        if user and (locale := user.get('language', '')):
            self.i18n.current_locale = locale.lower()  # Set current locale
            self.locale_mappings[telegram_id] = locale  # Store locale in mappings
            return locale

        state = data.get('state')
        if state:
            current_state = await state.get_state()
            locale = await super().get_locale(event=event, data=data)

            if current_state != 'StartChooseLanguage:active':
                message = self._extract_message(event)
                await self._initial_language_setup(message, state, locale)  # Initial setup for language selection
                raise StopLocaleMiddlewareProcessing

            return locale

        return await super().get_locale(event=event, data=data)

    async def get_lang(self, telegram_id):
        """
        Get the stored locale for a specific user.
        """
        return self.locale_mappings.get(telegram_id)

    async def set_locale(self, telegram_id: int, value: str):
        """
        Set the locale for a specific user and perform memory cleanup if necessary.
        """
        if datetime.now() >= self.next_cleanup_date:
            await self.memory_cleanup()  # Perform memory cleanup if the scheduled date is reached
        self.locale_mappings[telegram_id] = value  # Store the new locale in mappings

    async def _initial_language_setup(self, message, state, locale):
        """
        Initial setup for language selection process.

        Args:
            message: The message object from the event.
            state: The current state of the user.
            locale: The locale determined for the user.
        """
        await state.set_state(StartChooseLanguage.active)
        from app.services import process_choose_initial_language
        await process_choose_initial_language(message, locale)

    async def memory_cleanup(self):
        """
        Cleanup method to clear stored data such as locale mappings and tips.

        Resets the cleanup date to 30 days from the current date.
        """
        self.locale_mappings.clear()
        self.tip_mode.tips_count.clear()
        self.tip_mode.last_message.clear()
        self.next_cleanup_date = datetime.now() + timedelta(days=30)

    @staticmethod
    def _extract_message(event: TelegramObject):
        """
        Extracts the message object from the event, handling both messages and callback queries.
        """
        if isinstance(event.callback_query, CallbackQuery):
            return event.callback_query.message
        return event.message


# Instantiate the tips middleware and locale middleware
tip_mode = GettingStartedTips()
i18n_middleware = LocaleMiddleware(i18n=i18n, tip_mode=tip_mode)

# Add the locale middleware to the dispatcher
dp.update.middleware(i18n_middleware)
