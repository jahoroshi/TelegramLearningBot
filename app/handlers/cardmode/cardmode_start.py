import asyncio
from typing import Optional

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile
from aiogram.types import Message
from pydantic import ValidationError

import app.keyboards as kb
from app.handlers.cardmode.speech import get_sound
from app.handlers.start import cmd_start
# from app.middlewares import TestMiddleware
from app.requests import send_request
from app.services.cardmode import gen_output_text
from app.validators import StartConfigValidator, card_data_isvalid
from settings import BASE_URL

router = Router()


async def card_mode_start(message: Message, state: FSMContext, slug: Optional[str] = None,
                          study_mode: Optional[str] = None, study_format: Optional[str] = None):
    data_store = await state.get_data()
    try:
        StartConfigValidator(**data_store.get('start_config', {}))
    except ValidationError:
        try:
            tg_id = state.key.user_id

            if not slug and not study_mode:
                start_url = f'http://localhost:8000/study/api/v1/get_start_config/{tg_id}/'
            else:
                start_url = \
                    f'http://localhost:8000/study/api/v1/get_start_config/{slug}/{study_mode}/{study_format}/{tg_id}/'

            response = await send_request(start_url)
            start_config = response.get('data')
            StartConfigValidator(**start_config if start_config else {})
            await state.update_data(start_config=start_config)
        except ValidationError:
            print(f"Validation error after fetching new config in {__name__}")
            await message.answer('Something went wrong, try again.')
            await cmd_start(message, state)
            return
        except Exception as e:
            print(f'Error in {__name__}:  {e}')
            await message.answer('Something went wrong, try again.')
            await cmd_start(message, state)
            return

    await message.answer("Let's begin", reply_markup=await kb.mem_ratings())
    await card_mode(message=message, state=state)


# async def card_mode(message: Message, state: FSMContext, card_data: dict = None):
#     state_data = await state.get_data()
#     text_hint = "_Press 'Show Back' or choose a hint_" if card_data is None else ''
#
#     if not card_data:
#         url_get_card = state_data.get('start_config', {}).get('urls', {}).get('get_card')
#         if url_get_card:
#             response = await send_request(f'{BASE_URL}{url_get_card}')
#             card_data = response.get('data')
#             status = response.get('status')
#             if status // 100 != 2:
#                 await cmd_start(message, state)
#                 return
#         else:
#             await cmd_start(message, state)
#             return
#
#     if not card_data_isvalid(card_data):
#         if state_data:
#             study_mode = state_data.get('start_config', {}).get('study_mode')
#             action = 'studied' if study_mode == 'new' else 'reviewed'
#             text1 = '🎊 Congratulations! 🎊'
#             text2 = '🎉'
#             text3 = f'You have {action} all your cards for today.\nYou can study another deck or wait for the next review session.\n\n'
#             await message.answer(text1)
#             await asyncio.sleep(1)
#             await message.answer(text2)
#             await asyncio.sleep(1.5)
#             await message.answer(text3)
#             await asyncio.sleep(2)
#             await cmd_start(message, state)
#             return
#
#         await message.answer('Something went wrong, try again.')
#         await cmd_start(message, state)
#         return
#
#     await state.update_data(card_data=card_data)
#
#     start_config = state_data.get('start_config')
#     buttons_to_show = start_config['buttons_to_show']
#     is_first_show = card_data.get('ratings_count', {}).get('5')
#     front_side = card_data.get("front_side", '')
#     study_format = start_config.get('study_format')
#     msg_params = {'reply_markup': await kb.card_mode_buttons(buttons_to_show, is_first_show=is_first_show),
#                   'parse_mode': ParseMode.MARKDOWN_V2}
#     if study_format == 'audio':
#         mappings_id = card_data.get('mappings_id')
#         status, sound = await get_sound(start_config, mappings_id)
#         text_hint = "_Press 'Show Back' or choose a hint_"
#
#         if status // 100 == 2:
#             buttons_to_show['speech'] = False
#             msg_params['reply_markup'] = await kb.card_mode_buttons(buttons_to_show,
#                                                                     is_first_show=is_first_show)
#             text = gen_output_text(extra_text=text_hint)
#
#             file = BufferedInputFile(sound, filename='Play')
#             await message.answer_voice(file)
#             await message.answer(text, **msg_params)
#             return
#         else:
#             text = gen_output_text(front=front_side, extra_text=text_hint)
#     else:
#         text = gen_output_text(front=front_side, extra_text=text_hint)
#     await message.answer(text, **msg_params)


async def card_mode(message: Message, state: FSMContext, card_data: dict = None):
    state_data = await state.get_data()
    text_hint = "_Press 'Show Back' or choose a hint_" if card_data is None else ''

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
    url_get_card = state_data.get('start_config', {}).get('urls', {}).get('get_card')
    if url_get_card:
        response = await send_request(f'{BASE_URL}{url_get_card}')
        card_data = response.get('data')
        status = response.get('status')
        if status // 100 != 2:
            await cmd_start(message, state)
            return None
        return card_data
    else:
        await cmd_start(message, state)
        return None


async def handle_invalid_card_data(state_data, message, state):
    if state_data:
        study_mode = state_data.get('start_config', {}).get('study_mode')
        action = 'studied' if study_mode == 'new' else 'reviewed'
        text1 = '🎊 Congratulations! 🎊'
        text2 = '🎉'
        text3 = f'You have {action} all your cards for today.\nYou can study another deck or wait for the next review session.\n\n'
        await message.answer(text1)
        await asyncio.sleep(1)
        await message.answer(text2)
        await asyncio.sleep(1.5)
        await message.answer(text3)
        await asyncio.sleep(2)
        await cmd_start(message, state)
    else:
        await message.answer('Something went wrong, try again.')
        await cmd_start(message, state)


async def show_card(message, state, card_data, text_hint):
    state_data = await state.get_data()
    start_config = state_data.get('start_config')
    buttons_to_show = start_config['buttons_to_show']
    is_first_show = card_data.get('ratings_count', {}).get('5')
    front_side = card_data.get("front_side", '')
    study_format = start_config.get('study_format')
    msg_params = {'reply_markup': await kb.card_mode_buttons(buttons_to_show, is_first_show=is_first_show),
                  'parse_mode': ParseMode.MARKDOWN_V2}

    if study_format == 'audio':
        await handle_audio_format(start_config, card_data, message, msg_params, text_hint, is_first_show)
    else:
        text = gen_output_text(front=front_side, extra_text=text_hint)
        await message.answer(text, **msg_params)


async def handle_audio_format(start_config, card_data, message, msg_params, text_hint, is_first_show):
    mappings_id = card_data.get('mappings_id')
    status, sound = await get_sound(start_config, mappings_id)
    text_hint = "_Press 'Show Back' or choose a hint_"

    if status // 100 == 2:
        buttons_to_show = start_config['buttons_to_show']
        buttons_to_show['speech'] = False
        msg_params['reply_markup'] = await kb.card_mode_buttons(buttons_to_show, is_first_show=is_first_show)
        text = gen_output_text(extra_text=text_hint)

        file = BufferedInputFile(sound, filename='Play')
        await message.answer_voice(file, **msg_params)
        # await message.answer(text, **msg_params)
    else:
        front_side = card_data.get("front_side", '')
        text = gen_output_text(front=front_side, extra_text=text_hint)
        await message.answer(text, **msg_params)
