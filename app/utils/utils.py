import asyncio
import app.keyboards as kb

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommand, MenuButtonCommands, BotCommandScopeChat
from bot import bot
from app.middlewares.i18n_init import i18n

_ = i18n.gettext

async def display_message_and_redirect(message: Message, state: FSMContext, text):
    await message.answer(text, reply_markup=kb.refresh_button)
    await asyncio.sleep(1.5)
    from app.handlers import decks_list
    await decks_list(message, state)


async def set_user_commands(message: Message):
    user_commands = [
        BotCommand(command='addcard', description=_('add_card_quick')),
        BotCommand(command='newdeck', description=_('create_new_deck')),
        BotCommand(command='refresh', description=_('refresh_bot')),
        BotCommand(command='settings', description=_('manage_account_settings')),
        BotCommand(command='help', description=_('get_help_information')),
    ]

    await bot.set_my_commands(user_commands, scope=BotCommandScopeChat(chat_id=message.chat.id))
