from aiogram.utils.i18n import I18n, ConstI18nMiddleware
from pathlib import Path

CUR_DIR = Path(__file__).parent.parent.absolute()
i18n = I18n(path=f'{CUR_DIR}/locales')

