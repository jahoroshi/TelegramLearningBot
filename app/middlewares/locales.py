from typing import Dict, Any

from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18n, ConstI18nMiddleware

from bot import dp


class CustomI18nMiddleware(ConstI18nMiddleware):

    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        if self.locale == 'no':
            self.locale = 'ru'
        else:
            self.locale = 'en'
        return self.locale


i18n = I18n(path='app/locales')
mw = CustomI18nMiddleware(i18n=i18n, locale='init')
dp.update.middleware(mw)
_ = i18n.gettext
