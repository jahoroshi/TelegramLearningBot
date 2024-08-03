import asyncio

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import app.keyboards as kb
from app.middlewares.i18n_init import i18n
from app.services.bot import (
    generate_help_response,
    process_start_command,
    process_choose_initial_language,
    process_set_language_callback,
    process_to_decks_list,
    process_cmd_a,
)

# Initialize routers
router = Router()

# Define gettext
_ = i18n.gettext

@router.message(Command(commands=['help']))
async def get_help(message: Message):
    """
    Handler for the '/help' command. Calls the service function to generate a help response.
    """
    text, reply_markup = await generate_help_response()
    await message.answer(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)


@router.message(F.text.in_(('REFRESH', 'ОБНОВИТЬ')))
@router.message(Command(commands=['refresh']))
@router.message(CommandStart())
async def cmd_start(callback_or_message: Message | CallbackQuery, state: FSMContext):
    """
    Handler for the '/start' and '/refresh' commands.
    """
    await process_start_command(callback_or_message, state)


@router.message(F.text == 'a')
async def cmd_a(message: Message, state: FSMContext):
    """
    Handler for the 'a' command to send a formatted text message.
    """
    await process_cmd_a(message)


@router.callback_query(F.data.startswith('set_language_'))
async def handle_initial_user_language(callback: CallbackQuery, state: FSMContext):
    """
    Callback handler to set the initial user language.
    """
    await process_set_language_callback(callback, state)


async def to_decks_list(callback: CallbackQuery, state: FSMContext):
    """
    Navigate to the decks list.
    """
    await process_to_decks_list(callback, state)
