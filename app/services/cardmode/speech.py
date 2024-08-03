from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery

import app.keyboards as kb
from app.requests import send_request
from app.utils.cardmode import gen_output_text
from app.middlewares.i18n_init import i18n
from settings import BASE_URL

_ = i18n.gettext


async def process_text_to_speech(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    """
    Processes the text-to-speech conversion for the card's front side.

    Args:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The finite state machine context for the user.
        data_store (dict, optional): The data store containing card information. Defaults to None.
    """
    # Check if speech is locked
    if callback.data == 'button_speech_locked':
        await callback.answer(_('already_announced'))
        return

    card_data = data_store.get('card_data', {})
    start_config = data_store.get('start_config', {})

    # Lock the speech button and get updated button names
    buttons_to_show, update_button_names = await speech_lock(start_config)
    mappings_id = card_data.get('mappings_id')
    front_side = card_data.get("front_side")

    # Get sound for the card's front side
    status, sound = await get_sound(start_config, mappings_id)

    if status // 100 == 2:
        file = BufferedInputFile(sound, filename=front_side)
        text = gen_output_text(front=front_side)

        # Update the message with the text and play the sound
        await callback.message.edit_text(
            text,
            reply_markup=await kb.card_mode_buttons(buttons_to_show, update_names=update_button_names),
            parse_mode=ParseMode.HTML,
        )

        await callback.message.answer_voice(file)
    else:
        await callback.answer(_('text_to_speech_error'))


async def get_sound(start_config, mappings_id):
    """
    Retrieves sound data for a given card mapping ID.

    Args:
        start_config (dict): The start configuration containing URLs.
        mappings_id (str): The mappings ID for the card.

    Returns:
        tuple: A tuple containing the status and sound data.
    """
    url_get_sound = start_config.get('urls', {}).get('get_sound', '')
    url = url_get_sound.replace('dummy_mappings_id', str(mappings_id))
    response = await send_request(f"{BASE_URL}{url}")
    status = response.get('status')
    sound = response.get('data')
    return status, sound


async def speech_lock(start_config):
    """
    Locks the speech button to prevent multiple requests.

    Args:
        start_config (dict): The start configuration containing button settings.

    Returns:
        tuple: A tuple containing updated buttons to show and their names.
    """
    buttons_to_show = start_config.get('buttons_to_show', {}).copy()
    buttons_to_show.pop('speech', None)
    buttons_to_show['speech_locked'] = True
    update_button_names = {'speech_locked': '🔊'}
    return buttons_to_show, update_button_names
