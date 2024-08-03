import asyncio
import random
from typing import Optional

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile
from aiogram.types import Message
from pydantic import ValidationError

import app.keyboards as kb
from app.middlewares.i18n_init import i18n
from app.requests import send_request
from app.services.bot.start import process_start_command
from app.services.cardmode.speech import get_sound
from app.utils.cardmode import gen_output_text, emoji
from app.validators import StartConfigValidator, card_data_isvalid
from settings import BASE_URL

_ = i18n.gettext


async def process_card_mode_start(message: Message, state: FSMContext, slug: Optional[str] = None,
                                  study_mode: Optional[str] = None, study_format: Optional[str] = None):
    """
    Initiates the card mode session by setting up the necessary configurations.

    Args:
        message (Message): The message object from the user.
        state (FSMContext): The finite state machine context for the user.
        slug (Optional[str]): The slug identifier for the study session. Defaults to None.
        study_mode (Optional[str]): The study mode (e.g., 'review', 'new'). Defaults to None.
        study_format (Optional[str]): The study format (e.g., 'text', 'audio'). Defaults to None.
    """
    data_store = await state.get_data()
    try:
        # Validate start configuration
        StartConfigValidator(**data_store.get('start_config', {}))
    except ValidationError:
        try:
            tg_id = state.key.user_id

            if not slug and not study_mode:
                start_url = f'{BASE_URL}/study/api/v1/get_start_config/{tg_id}/'
            else:
                start_url = \
                    f'{BASE_URL}/study/api/v1/get_start_config/{slug}/{study_mode}/{study_format}/{tg_id}/'

            response = await send_request(start_url)
            start_config = response.get('data')
            # Validate fetched start configuration
            StartConfigValidator(**start_config if start_config else {})
            await state.update_data(start_config=start_config)
        except ValidationError:
            print(f"Validation error after fetching new config in {__name__}")
            await message.answer(_('try_again_error'))
            await process_start_command(message, state)
            return
        except Exception as e:
            print(f'Error in {__name__}:  {e}')
            await message.answer(_('try_again_error'))
            await process_start_command(message, state)
            return

    await message.answer(_("let's_begin"), reply_markup=await kb.mem_ratings())
    await process_card_mode(message=message, state=state)


async def process_card_mode(message: Message, state: FSMContext, card_data: dict = None):
    """
    Processes the card mode session by fetching and validating card data.

    Args:
        message (Message): The message object from the user.
        state (FSMContext): The finite state machine context for the user.
        card_data (dict, optional): The card data to process. Defaults to None.
    """
    state_data = await state.get_data()
    text_hint = _("show_back_hint") if card_data is None else ''

    if not card_data:
        card_data = await fetch_card_data(state_data, message, state)
        if card_data is None:
            return

    if not card_data_isvalid(card_data):
        await handle_invalid_card_data(state_data, message, state)
        return

    await state.update_data(card_data=card_data)
    await show_card(message, state, card_data, text_hint)


async def fetch_card_data(state_data, message, state):
    """
    Fetches card data from the server.

    Args:
        state_data (dict): The state data from FSM context.
        message (Message): The message object from the user.
        state (FSMContext): The finite state machine context for the user.

    Returns:
        dict: The fetched card data.
    """
    url_get_card = state_data.get('start_config', {}).get('urls', {}).get('get_card')
    if url_get_card:
        response = await send_request(f'{BASE_URL}{url_get_card}')
        card_data = response.get('data')
        status = response.get('status')
        if status // 100 != 2:
            await process_start_command(message, state)
            return None
        return card_data
    else:
        await process_start_command(message, state)
        return None


async def handle_invalid_card_data(state_data, message, state):
    """
    Handles cases where card data is invalid.

    Args:
        state_data (dict): The state data from FSM context.
        message (Message): The message object from the user.
        state (FSMContext): The finite state machine context for the user.
    """
    if state_data:
        study_mode = state_data.get('start_config', {}).get('study_mode')
        action = _('studied') if study_mode == 'new' else _('reviewed')
        text1 = _('congratulations')
        text2 = '🎉'
        text3 = _('all_cards_studied').format(action)
        await message.answer(text1)
        await asyncio.sleep(1)
        await message.answer(text2)
        await asyncio.sleep(1.5)
        await message.answer(text3)
        await asyncio.sleep(2)
        await process_start_command(message, state)
    else:
        await message.answer(_('try_again_error'))
        await process_start_command(message, state)


async def show_card(message, state, card_data, text_hint):
    """
    Displays the card to the user based on the study format.

    Args:
        message (Message): The message object from the user.
        state (FSMContext): The finite state machine context for the user.
        card_data (dict): The card data to display.
        text_hint (str): The text hint to show to the user.
    """
    state_data = await state.get_data()
    start_config = state_data.get('start_config')
    buttons_to_show = start_config['buttons_to_show']
    is_first_show = card_data.get('ratings_count', {}).get('5')
    front_side = card_data.get("front_side", '')
    study_format = start_config.get('study_format')
    msg_params = {'reply_markup': await kb.card_mode_buttons(buttons_to_show, is_first_show=is_first_show),
                  'parse_mode': ParseMode.HTML}

    if study_format == 'audio':
        await handle_audio_format(start_config, card_data, message, msg_params, text_hint, is_first_show)
    else:
        text = gen_output_text(front=front_side, extra_text=text_hint)
        await message.answer(text, **msg_params)


async def handle_audio_format(start_config, card_data, message, msg_params, text_hint, is_first_show):
    """
    Handles the audio format for displaying card data.

    Args:
        start_config (dict): The start configuration for the session.
        card_data (dict): The card data to display.
        message (Message): The message object from the user.
        msg_params (dict): The message parameters for the response.
        text_hint (str): The text hint to show to the user.
        is_first_show (bool): Flag to indicate if it is the first time showing the card.
    """

    mappings_id = card_data.get('mappings_id')
    status, sound = await get_sound(start_config, mappings_id)
    text_hint = random.choice(emoji) if not text_hint else text_hint

    if status // 100 == 2:
        buttons_to_show = start_config['buttons_to_show']
        buttons_to_show['speech'] = False
        msg_params['reply_markup'] = await kb.card_mode_buttons(buttons_to_show, is_first_show=is_first_show)
        text = gen_output_text(extra_text=text_hint)

        file = BufferedInputFile(sound, filename='Play')
        await message.answer_voice(file)
        await message.answer(text, **msg_params)
    else:
        front_side = card_data.get("front_side", '')
        text = gen_output_text(front=front_side, extra_text=text_hint)
        await message.answer(text, **msg_params)
