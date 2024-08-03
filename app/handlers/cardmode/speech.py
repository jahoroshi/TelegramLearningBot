from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile
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

@router.callback_query(F.data.in_(('button_speech', 'button_speech_locked')))
@check_card_data
async def text_to_speech(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    if callback.data == 'button_speech_locked':
        await callback.answer(_('already_announced'))
        return
    card_data = data_store.get('card_data', {})
    start_config = data_store.get('start_config', {})

    buttons_to_show, update_button_names = await speech_lock(start_config)
    mappings_id = card_data.get('mappings_id')
    front_side = card_data.get("front_side")
    status, sound = await get_sound(start_config, mappings_id)
    if status // 100 == 2:
        file = BufferedInputFile(sound, filename=front_side)
        text = gen_output_text(front=front_side)

        await callback.message.edit_text(
            text,
            reply_markup=await kb.card_mode_buttons(buttons_to_show, update_names=update_button_names),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

        await callback.message.answer_voice(file)
    else:
        await callback.answer(_('text_to_speech_error'))


async def get_sound(start_config, mappings_id):
    url_get_sound = start_config.get('urls', {}).get('get_sound', '')
    url = url_get_sound.replace('dummy_mappings_id', str(mappings_id))
    response = await send_request(f"{BASE_URL}{url}")
    status = response.get('status')
    sound = response.get('data')
    return status, sound


async def speech_lock(start_config):
    buttons_to_show = start_config.get('buttons_to_show', {}).copy()
    buttons_to_show.pop('speech')
    buttons_to_show['speech_locked'] = True
    update_button_names = {'speech_locked': '🔊'}
    return buttons_to_show, update_button_names
