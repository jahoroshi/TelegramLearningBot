import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import app.keyboards as kb


async def display_message_and_redirect(message: Message, state: FSMContext, text):
    await message.answer(text, reply_markup=kb.studying_start)
    await asyncio.sleep(1.5)
    from app.handlers import decks_list
    await decks_list(message, state)