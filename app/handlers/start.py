import asyncio
import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message

import app.keyboards as kb
from app.requests import send_request
from settings import BASE_URL

router = Router()


@router.message(CommandStart())
@router.callback_query(F.data == 'to_main')
@router.message(F.text == 'REFRESH')
async def cmd_start(message: Message, state: FSMContext = None):
    # может приходить callback, сделать обработку!!!!!!!
    telegram_id = state.key.user_id
    url = f'{BASE_URL}/users/api/v1/manage/{telegram_id}/'
    response = await send_request(url, method='GET')
    if response.get('status') == 200:
        try:
            data = response.get('data')
        except Exception as e:
            logging.error(f"In {__name__}:  Connection error while reading JSON: {e}")
            await message.answer("Не удалось получить данные с сервера. Попробуйте позже.")
            return
        from app.handlers import decks_list
        if data.get('language'):
            await decks_list(message, state)
        else:
            await decks_list(message, state)

    elif response.get('status') == 201:
        user_language = message.from_user.language_code
        messages = {
            'ru': 'Нажмите продолжить, если ваш язык русский',
            'en': 'Press continue if your language is English'
        }
        selected_language = 'ru' if user_language == 'ru' else 'en'
        opposite_language = 'en' if selected_language == 'ru' else 'ru'
        await message.answer(messages[selected_language], reply_markup=await kb.choose_language(selected_language))
        await asyncio.sleep(1.5)
        await message.answer(messages[opposite_language], reply_markup=await kb.choose_language(opposite_language))


@router.callback_query(F.data.startswith('set_language_'))
async def set_language(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    language = callback.data.split('_')[-1]
    telegram_id = state.key.user_id
    url = f'{BASE_URL}/users/api/v1/manage/{telegram_id}/'
    response = await send_request(url, method='PUT', data={'telegram_id': telegram_id, 'language': language})
    from app.handlers import decks_list
    await decks_list(callback.message, state)
