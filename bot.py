import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.methods import TelegramMethod, AnswerCallbackQuery
from aiogram.methods.base import TelegramType
from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18n, ConstI18nMiddleware
from dotenv import load_dotenv
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoggingSession(AiohttpSession):
    async def make_request(self, bot: Bot, method: TelegramMethod[TelegramType], timeout: Optional[int] = None):
        # if isinstance(method, AnswerCallbackQuery):
        # logger.info(f'------------------------------------------>> {datetime.now()}')
        # print(method)
        return await super().make_request(bot, method, timeout)


load_dotenv()
bot = Bot(token=os.getenv("TOKEN"), session=LoggingSession())
dp = Dispatcher()


