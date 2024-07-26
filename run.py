import asyncio
import logging

from aiogram import types
from aiogram.methods import SetChatMenuButton
from aiogram.types import BotCommand
from aiogram.types import BotCommandScopeDefault
from dotenv import load_dotenv

from app.handlers import main_router
from bot import bot, dp


async def main():
    # logging.info("Starting async_main to create tables")
    # await async_main()
    # logging.info("Tables created successfully")
    load_dotenv()
    dp.include_router(main_router)
    logging.info("Starting bot polling")

    # user_commands = [
    #     BotCommand(command='for', description='Описание команды /for'),
    #     BotCommand(command='magik', description='Описание команды /magik')
    # ]
    # await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())
    # menu_button = types.MenuButtonCommands(commands=user_commands)
    # res = await bot(SetChatMenuButton(menu_button=menu_button))
    # logging.info(res)
    # dp.middleware.setup(i18n_middleware.I18nMiddleware(i18n))
    await dp.start_polling(bot)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
