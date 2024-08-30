from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

import app.keyboards as kb
from app.requests import send_request
from app.utils.cardmode import gen_output_text
from app.middlewares.i18n_init import i18n
from settings import BASE_URL

_ = i18n.gettext


async def process_show_similar(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    """
    Processes the request to show similar words for the card's back side.

    Args:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The finite state machine context for the user.
        data_store (dict, optional): The data store containing card information. Defaults to None.
    """
    card_data = data_store.get('card_data')
    url_similar_words = data_store.get('start_config', {}).get('urls', {}).get('get_similar_with_telegram_id', '')
    mappings_id = card_data.get('mappings_id', '')
    telegram_id = state.key.user_id

    url = url_similar_words.replace('dummy_mappings_id', str(mappings_id)).replace(
        'dummy_telegram_id', str(telegram_id)
    )

    # Send request to get similar words
    response = await send_request(f"{BASE_URL}{url}")
    similar_words_data = response.get('data')
    status = response.get('status')

    if status // 100 == 2 and similar_words_data:
        front_side = card_data.get("front_side")
        text = gen_output_text(front=front_side)
        await callback.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=await kb.similar_words_output(similar_words_data)
        )
    else:
        await callback.answer(_('similar_words_not_found'))


async def process_similar_answer_check(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    """
    Processes the logic to check the user's answer against the correct answer.

    Args:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The finite state machine context for the user.
        data_store (dict, optional): The data store containing card information. Defaults to None.
    """
    card_data = data_store.get('card_data')
    user_answer = callback.data.split('_')[1]
    right_answer = card_data.get("back_side")

    # Determine if the user's answer is correct
    if user_answer == 'correct':
        await callback.message.delete()
        extra_text = _('correct_message')
        text = gen_output_text(card_data=card_data, extra_text=extra_text)
        await callback.message.answer(text, parse_mode=ParseMode.HTML)
    else:
        # Handle incorrect answers
        text = gen_output_text(front=card_data.get("front_side"))
        await callback.message.edit_text(text, parse_mode=ParseMode.HTML)
        await callback.message.answer(_('correct_answer').format(right_answer), parse_mode=ParseMode.HTML)
