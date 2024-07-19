import asyncio

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.utils.i18n import I18n

import app.keyboards as kb
from app.requests import send_request
from app.services import set_user_commands
from bot import i18n
from settings import BASE_URL

router = Router()


@router.message(CommandStart())
@router.callback_query(F.data == 'to_main')
@router.message(F.text == 'REFRESH')
async def cmd_start(message: Message, state: FSMContext = None):
    # может приходить callback, сделать обработку!!!!!!!
    if isinstance(message, CallbackQuery):
        message = message.message
    telegram_id = state.key.user_id if state else message.from_user.id
    url = f'{BASE_URL}/users/api/v1/manage/{telegram_id}/'
    response = await send_request(url, method='GET')
    if response.get('status') == 200:
        from app.handlers import decks_list
        if lang := response.get('data', {}).get('language'):
            # i18n = I18n(path='app/locales', default_locale=lang)

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

    await set_user_commands(message)


@router.callback_query(F.data.startswith('set_language_'))
async def set_language(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    language = callback.data.split('_')[-1]
    telegram_id = state.key.user_id
    url = f'{BASE_URL}/users/api/v1/manage/{telegram_id}/'
    response = await send_request(url, method='PUT', data={'telegram_id': telegram_id, 'language': language})
    from app.handlers import decks_list
    await decks_list(callback.message, state)


@router.message(Command('q'))
async def sandbox(message: Message, state: FSMContext):
    a = i18n.gettext('greeting')
    await message.reply(a)
@router.message(Command('qq'))
async def sandbox(message: Message, state: FSMContext):
    a = i18n.gettext('greeting')
    await message.reply(a)
