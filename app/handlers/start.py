import asyncio

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message

import app.keyboards as kb
from app.middlewares.locales import i18n, i18n_middleware
from app.requests import send_request
from app.services import set_user_commands, set_initial_user_language
from app.services.middleware import set_tips_middleware
from settings import BASE_URL

router = Router()
_ = i18n.gettext


@router.message(CommandStart())
@router.callback_query(F.data == 'to_main')
async def cmd_start(callback_or_message: Message or CallbackQuery, state: FSMContext):
    message = callback_or_message.message if isinstance(callback_or_message, CallbackQuery) else callback_or_message
    await set_user_commands(message)
    from app.handlers import decks_list
    await decks_list(message, state)


@router.message(F.text == 'REFRESH')
@router.message(Command(commands=['refresh']))

async def cmd_refresh(message: Message, state: FSMContext):
    has_language = await i18n_middleware.process_event(message, state)
    if has_language:
        await cmd_start(message, state)


async def choose_initial_language(message: Message):
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
async def handle_initial_user_language(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    current_state = await state.get_state()
    if current_state == 'StartChooseLanguage:active':
        language = callback.data.split('_')[-1]
        telegram_id = state.key.user_id
        await state.clear()

        response = await set_initial_user_language(telegram_id, language)
        if response.get('status') != 200:
            await to_decks_list(callback, state)
            return

        url = f'{BASE_URL}/deck/api/v1/manage/first_filling/{telegram_id}/{language}'
        response = await send_request(url, method='GET')
        if response and response.get('status') == 201:
            tips_middleware_instance = await set_tips_middleware()
            await callback.message.answer(_('greeting_after_creating_test_deck'))
            await asyncio.sleep(4)

            await to_decks_list(callback, state)

            tip_message = await callback.message.answer(_('tip_message_1'))
            tips_middleware_instance.last_msg = tip_message.message_id
        else:
            await to_decks_list(callback, state)


async def to_decks_list(callback: CallbackQuery, state: FSMContext):
    from app.handlers import decks_list
    await decks_list(callback.message, state)
