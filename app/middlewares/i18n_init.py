from pathlib import Path

from aiogram.utils.i18n import I18n

CUR_DIR = Path(__file__).parent.parent.absolute()
i18n = I18n(path=f'{CUR_DIR}/locales')

