from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.middlewares.locales import i18n
from app.requests import send_request
from app.services import display_message_and_redirect, DeckCreate
from settings import BASE_URL

_ = i18n.gettext
router = Router()


@router.message(Command(commands=['newdeck']))
@router.message(F.text == 'Create deck')
@router.callback_query(F.data == 'deck_create')
async def deck_create(callback_or_message: CallbackQuery or Message, state: FSMContext):
    if isinstance(callback_or_message, CallbackQuery):
        await callback_or_message.answer()
        message = callback_or_message.message
    else:
        message = callback_or_message
    text = 'Enter new deck\'s name'
    await message.answer(text, reply_markup=await kb.back())
    await state.set_state(DeckCreate.name)


@router.message(DeckCreate.name)
async def deck_create_handler(message: Message, state: FSMContext):
    name = message.text
    telegram_id = state.key.user_id
    data = {
        'name': name,
        'telegram_id': telegram_id,
    }
    url = f'{BASE_URL}/deck/api/v1/manage/'
    response = await send_request(url, method='POST', data=data)

    if response.get('status') == 201:
        text = '🎉 Deck was successfully created.'
    else:
        text = 'Something went wrong.'
    await display_message_and_redirect(message, state, text)
