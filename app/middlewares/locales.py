from pathlib import Path
from typing import Dict, Any

from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import I18n, ConstI18nMiddleware

from app.services import StartChooseLanguage
from app.services import get_or_create_user
from bot import dp

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomI18nMiddleware(ConstI18nMiddleware):
    async def __call__(self, handler, event: types.Update, data: Dict[str, Any]):
        if self.locale == 'init':
            logger.info(f"Locale initialized: {self.locale}")
            message = event.callback_query.message if isinstance(event.callback_query, CallbackQuery) else event.message
            state = data['state']
            has_language = await self.process_event(message, state)
            if has_language is False:
                return
        return await handler(event, data)

    async def process_event(self, message, state):

            telegram_id = state.key.user_id
            telegram_username = message.chat.username

            user = await get_or_create_user(telegram_id, telegram_username)
            if user:
                language = user.get('language')
                if language:
                    self.locale = language
                    I18n.current_locale = language
                    return True
                else:
                    await self._initial_language_setup(message, state)
                    return False

    async def _initial_language_setup(self, message, state):
        self.locale = message.from_user.language_code or 'en'
        await state.set_state(StartChooseLanguage.active)
        from app.handlers import choose_initial_language
        await choose_initial_language(message)

    async def set_locale(self, value: Any):
        self.locale = value


CUR_DIR = Path(__file__).parent.parent.absolute()
i18n = I18n(path=f'{CUR_DIR}/locales')
i18n_middleware = CustomI18nMiddleware(i18n=i18n, locale='init')
dp.update.middleware(i18n_middleware)
