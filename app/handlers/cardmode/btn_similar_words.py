from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

import app.keyboards as kb
# from app.middlewares import TestMiddleware
from app.requests import send_request
from app.utils.cardmode import gen_output_text
from app.utils.decorators import check_card_data

from app.middlewares.i18n_init import i18n
from settings import BASE_URL

router = Router()

_ = i18n.gettext

@router.callback_query(F.data == 'button_show_similar')
@check_card_data
async def show_similar(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    card_data = data_store.get('card_data')
    url_similar_words = data_store.get('start_config', {}).get('urls', {}).get('get_similar_words', '')
    mappings_id = card_data.get('mappings_id', '')
    url = url_similar_words.replace('dummy_mappings_id', str(mappings_id))
    response = await send_request(f"{BASE_URL}{url}")
    similar_words_data = response.get('data')
    status = response.get('status')
    if status // 100 == 2 and similar_words_data:
        front_side = card_data.get("front_side")
        text = gen_output_text(front=front_side)
        await callback.message.edit_text(
            text,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=await kb.similar_words_output(similar_words_data)
        )
    else:
        await callback.answer(_('similar_words_not_found'))


@router.callback_query(F.data.startswith('similar_'))
@check_card_data
async def similar_answer_check(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    card_data = data_store.get('card_data')
    user_answer = callback.data.split('_')[1]
    right_answer = card_data.get("back_side")
    if user_answer == 'correct':
        await callback.message.delete()
        extra_text = _('correct_message')
        text = gen_output_text(card_data=card_data, extra_text=extra_text)
        await callback.message.answer(text, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        text = gen_output_text(front=card_data.get("front_side"))
        await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN_V2)
        await callback.message.answer(_('correct_answer').format(right_answer))
