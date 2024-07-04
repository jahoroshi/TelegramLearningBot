import asyncio
import logging
import os
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram import Bot, Dispatcher, F
from config import TOKEN
from dotenv import load_dotenv
from app.handlers import main_router
from app.database.models import async_main
from bot import bot, dp



async def main():
    # logging.info("Starting async_main to create tables")
    # await async_main()
    # logging.info("Tables created successfully")
    load_dotenv()
    dp.include_router(main_router)
    logging.info("Starting bot polling")
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
