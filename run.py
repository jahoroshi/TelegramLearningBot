import asyncio
import logging

from aiogram import types
from aiogram.methods import SetChatMenuButton
from aiogram.types import BotCommand
from aiogram.types import BotCommandScopeDefault
from dotenv import load_dotenv

from app.handlers import main_router
from app.middlewares import TestMiddleware, LocaleMiddleware, i18n, GettingStartedTips
from bot import bot, dp


async def main():

    load_dotenv()
    mw = TestMiddleware()
    main_router.message.middleware(mw)
    main_router.callback_query.middleware(mw)


    dp.include_router(main_router)
    logging.info("Starting bot polling")

    await dp.start_polling(bot)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
