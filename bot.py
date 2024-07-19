import os
from typing import Dict, Any

from aiogram import Bot, Dispatcher
from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18n, ConstI18nMiddleware
from dotenv import load_dotenv

load_dotenv()
bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher()


