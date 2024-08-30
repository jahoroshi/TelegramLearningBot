from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

import app.keyboards as kb
from app.requests import send_request
from app.utils.cardmode import gen_output_text
from app.middlewares.i18n_init import i18n
from settings import BASE_URL

_ = i18n.gettext

async def process_ask_for_hint_chatgpt(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    card_data = data_store.get('card_data')
    url_openai_client = data_store.get('start_config', {}).get('urls', {}).get('get_hint_with_telegram_id', '')
    mappings_id = card_data.get('mappings_id', '')
    telegram_id = state.key.user_id
    url = url_openai_client.replace('dummy_mappings_id', str(mappings_id)).replace(
        'dummy_telegram_id', str(telegram_id)
    )

    response = await send_request(f"{BASE_URL}{url}")
    message = response.get('data')
    status = response.get('status')

    if status // 100 == 2 and message:
        start_config = data_store.get('start_config')
        buttons_to_show = start_config['buttons_to_show']
        front = card_data.get("front_side")
        text = f'<b>ChatGPT:</b>\n{message}'
        params = {
            'text': gen_output_text(front=front, extra_text=text),
            'parse_mode': ParseMode.HTML,
            'reply_markup': await kb.card_mode_buttons(buttons_to_show)
        }

        await callback.message.edit_text(**params)
    else:
        await callback.answer(_('no_message_from_chatgpt'))