import asyncio

from aiogram.enums import ParseMode

import app.keyboards as kb

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommand, MenuButtonCommands, BotCommandScopeChat
from bot import bot
from app.middlewares.i18n_init import i18n

_ = i18n.gettext

async def display_message_and_redirect(message: Message, state: FSMContext, text):
    await message.answer(text, parse_mode=ParseMode.HTML)
    await asyncio.sleep(1.5)
    from app.services import handle_decks_list_request
    await handle_decks_list_request(message, state)


async def set_user_commands(message: Message):
    user_commands = [
        BotCommand(command='newdeck', description=_('create_new_deck')),
        BotCommand(command='addcard', description=_('add_card_quick')),
        BotCommand(command='settings', description=_('manage_account_settings')),
        BotCommand(command='help', description=_('get_help_information')),
        BotCommand(command='refresh', description=_('refresh_bot')),
    ]

    await bot.set_my_commands(user_commands, scope=BotCommandScopeChat(chat_id=message.chat.id))
