import asyncio

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message

import app.keyboards as kb
from app.middlewares.locales import i18n

from app.requests import send_request
from app.services import set_user_commands, set_initial_user_language
from settings import BASE_URL

router = Router()
_ = i18n.gettext

@router.message(CommandStart())
@router.callback_query(F.data == 'to_main')
@router.message(F.text == 'REFRESH')
async def cmd_start(callback_or_message: Message or CallbackQuery, state: FSMContext):
    message = callback_or_message.message if isinstance(callback_or_message, CallbackQuery) else callback_or_message
    await set_user_commands(message)
    from app.handlers import decks_list
    await decks_list(message, state)


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
        if response.get('status') == 200:
            telegram_id = state.key.user_id
            url = f'{BASE_URL}/deck/api/v1/manage/first_filling/{telegram_id}/{language}'
            response = await send_request(url, method='GET')
            if response and response.get('status') == 201:
                text = _('greeting_after_creating_test_deck')
                await callback.message.answer(text)
                await asyncio.sleep(2)

        from app.handlers import decks_list
        await decks_list(callback.message, state)


# @router.message(Command('q'))
# async def sandbox(message: Message, state: FSMContext):
#     i18n_middleware.set_locale('ru')
#
#     a = i18n.gettext('greeting')
#     await message.reply(a)
#
#
# @router.message(Command('qq'))
# async def sandbox(message: Message, state: FSMContext):
#     i18n_middleware.set_locale('en')
#
#     a = i18n.gettext('greeting')
#     await message.reply(a)
