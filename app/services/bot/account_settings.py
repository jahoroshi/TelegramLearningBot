import asyncio

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import app.keyboards as kb
from app.middlewares.locales import i18n, i18n_middleware
from app.requests import send_request
from app.states import StartChooseLanguage
from app.utils import set_user_commands, set_initial_user_language, display_message_and_redirect
# from app.utils.middleware import start_tips_middleware
from settings import BASE_URL

_ = i18n.gettext



async def process_account_settings(message: Message, state: FSMContext):
    text = _('account_settings')
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=await kb.account_settings())

async def process_change_language(callback_query: CallbackQuery, state: FSMContext):
    text = _('language_selection')
    await callback_query.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=await kb.change_language())

async def process_change_language_handler(callback_query: CallbackQuery, state: FSMContext):
    language = callback_query.data.split('_')[-1]
    telegram_id = state.key.user_id
    response = await set_initial_user_language(telegram_id, language.upper())

    if response.get('status') == 200:
        lang = await i18n_middleware.get_lang(telegram_id)
        is_lower = lang.islower()
        language = language if is_lower else language.upper()
        await i18n_middleware.set_locale(telegram_id, language)
        text = _('language_changed_success')
    else:
        text = _('language_changed_failure')

    await display_message_and_redirect(callback_query.message, state, text)

