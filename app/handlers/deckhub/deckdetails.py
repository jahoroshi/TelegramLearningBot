from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.middlewares.i18n_init import i18n
from app.requests import send_request
from app.utils import create_deck_info, clear_current_state
from settings import BASE_URL

_ = i18n.gettext
router = Router()


@router.callback_query(F.data.startswith('deck_details_'))
@clear_current_state
async def deck_details(callback_or_message: CallbackQuery or Message, state: FSMContext, slug=None):
    if isinstance(callback_or_message, CallbackQuery):
        message = callback_or_message.message
        slug = callback_or_message.data.split('_')[-1]
    else:
        message = callback_or_message
    url = f'{BASE_URL}/deck/api/v1/manage/{slug}/'
    response = await send_request(url)
    if response.get('status') == 200:
        data = response.get('data')
        text = await create_deck_info(data)
        await message.edit_text(text, parse_mode=ParseMode.MARKDOWN_V2,
                                reply_markup=await kb.manage_deck(data))
