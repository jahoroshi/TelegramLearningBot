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
    def __init__(
            self,
            i18n: I18n,
            tip_mode: GettingStartedTips,
            i18n_key: Optional[str] = "i18n",
            middleware_key: str = "i18n_middleware",
    ) -> None:
        super().__init__(i18n=i18n, i18n_key=i18n_key, middleware_key=middleware_key)
        self.locale_mappings: Dict[int, str] = {}
        self.tip_mode = tip_mode
        self.next_cleanup_date = datetime.now() + timedelta(days=30)

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:

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

        if current_locale.isupper():
            try:
                await self.tip_mode.process_tip_message(event, data, current_locale.lower())
            except DisableTipModeForUser as e:
                await self.set_locale(e.user_id, current_locale.lower())

        return event_handler

    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        event_from_user: Optional[User] = data.get("event_from_user", None)
        telegram_id = event_from_user.id
        locale = self.locale_mappings.get(telegram_id)

        if locale:
            return locale

        telegram_username = event_from_user.username
        user = await get_or_create_user(telegram_id, telegram_username)

        if user and (locale := user.get('language', '')):
            # I18n.current_locale = locale
            self.i18n.current_locale = locale.lower()
            self.locale_mappings[telegram_id] = locale
            return locale

        state = data.get('state')
        if state:
            current_state = await state.get_state()
            locale = await super().get_locale(event=event, data=data)

            if current_state != 'StartChooseLanguage:active':
                message = self._extract_message(event)
                await self._initial_language_setup(message, state, locale)
                raise StopLocaleMiddlewareProcessing

            return locale

        return await super().get_locale(event=event, data=data)

    async def get_lang(self, telegram_id):
        return self.locale_mappings.get(telegram_id)

    async def set_locale(self, telegram_id: int, value: str):
        if datetime.now() >= self.next_cleanup_date:
            await self.memory_cleanup()
        self.locale_mappings[telegram_id] = value

    async def _initial_language_setup(self, message, state, locale):
        await state.set_state(StartChooseLanguage.active)
        from app.services import process_choose_initial_language
        await process_choose_initial_language(message, locale)

    async def memory_cleanup(self):
        self.locale_mappings.clear()
        self.tip_mode.tips_count.clear()
        self.tip_mode.last_message.clear()
        self.next_cleanup_date = datetime.now() + timedelta(days=30)


    @staticmethod
    def _extract_message(event: TelegramObject):
        if isinstance(event.callback_query, CallbackQuery):
            return event.callback_query.message
        return event.message


tip_mode = GettingStartedTips()
i18n_middleware = LocaleMiddleware(i18n=i18n, tip_mode=tip_mode)

dp.update.middleware(i18n_middleware)
