import asyncio
import app.keyboards as kb

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommand, MenuButtonCommands, BotCommandScopeChat
from bot import bot


async def display_message_and_redirect(message: Message, state: FSMContext, text):
    await message.answer(text, reply_markup=kb.refresh_session)
    await asyncio.sleep(1.5)
    from app.handlers import decks_list
    await decks_list(message, state)


async def set_user_commands(message: Message):
    user_commands = [
        BotCommand(command='newdeck', description='Create a new deck'),
        BotCommand(command='start', description='Go to the start menu'),
    ]

    menu_button = MenuButtonCommands(commands=user_commands)
    res = await bot.set_my_commands(user_commands, scope=BotCommandScopeChat(chat_id=message.chat.id))
    print(res)
