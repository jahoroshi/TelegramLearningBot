import asyncio
import time
from itertools import chain

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

import app.keyboards as kb
from app.handlers import decks_list
from app.requests import send_request
from app.services import check_current_state, display_message_and_redirect, ImportCards, CardManage
from settings import BASE_URL

router = Router()


@router.callback_query(F.data.startswith('import_cards_'))
@check_current_state
async def import_cards(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(ImportCards.data)
    slug = callback.data.split('_')[-1]
    await state.update_data(slug=slug)
    await callback.message.edit_text(
        f'''🔔 *Import instruction:*
» Max lenght message 4096 chars\.\n
» Use semicolon * \; * as separator between sides\n
» Each card must be on a new line\.

*Example\:*
>\(_front side_\) *\;* \(_back side_\)
>{f"Apple":^14} *\;* {f"Яблоко":^11}
>{f"Orange":^12} *\;* {f"Апельсин":^11}

_enter text or press back for cansel_
''', parse_mode=ParseMode.MARKDOWN_V2, reply_markup=await kb.back_to_decklist_or_deckdetails(slug))


@router.message(ImportCards.data)
async def import_cards_handler(message: Message, state: FSMContext):
    cards = message.text
    data = await state.get_data()
    slug = data.get('slug')
    cards_data = {
        'text': cards,
        'cards_separator': 'new_line',
        'words_separator': 'semicolon',
        'words_separator_custom': '',
        'cards_separator_custom': '',
    }
    url = f'{BASE_URL}/cards/api/v1/import_cards/{slug}/'
    response = await send_request(url, method='POST', data=cards_data)
    status = response.get('status')
    if status == 201:
        text = response.get('data', {}).get('detail')
    else:
        text = '❗️ Something went wrong.'
    await message.answer(text, reply_markup=await kb.back_to_decklist_or_deckdetails(slug))
    # await asyncio.sleep(1)
    # await decks_list(message, state)


@router.callback_query(F.data.startswith('add_card_'))
@check_current_state
async def card_create_begin(callback: CallbackQuery, state: FSMContext):
    slug = callback.data.split('_')[-1]
    await state.set_state(CardManage.front_side)
    await state.update_data(card_ops_state='create')
    await state.update_data(slug=slug)
    await callback.message.edit_reply_markup(reply_markup=await kb.back_to_decklist_or_deckdetails(slug))
    await callback.message.answer('☝️ Enter front side\n>Or press    *back*   for cansel',
                                  parse_mode=ParseMode.MARKDOWN_V2, reply_markup=ReplyKeyboardRemove())


@router.callback_query(F.data.startswith('show_cards_'))
@check_current_state
async def show_cards(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    slug = callback.data.split('_')[-1]
    tg_id = state.key.user_id
    url = f'{BASE_URL}/deck/api/v1/manage/{tg_id}/{slug}/'
    response = await send_request(url, method='GET')
    status = response.get('status')
    if status == 200:
        data = response.get('data', {})
        cards_id_index = {}
        cards_list = ''
        for index, card in enumerate(data, 1):
            cards_id_index[index] = card.get('id')
            cards_list += f'» {index}. {card.get("side1")} ¦ {card.get("side2")}\n'
        if len(cards_list) != 0:
            await callback.message.edit_text(cards_list, reply_markup=await kb.show_cards_action_buttons(slug))
            await state.set_state(CardManage.card_ops_state)
            await state.update_data(cards_id_index=cards_id_index, slug=slug)
        else:
            await callback.message.answer('📂 The deck is empty.')
            await asyncio.sleep(1.5)
            await decks_list(callback.message, state)

    else:
        text = '❗️ Something went wrong.'
        await callback.message.answer(text, reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(1.5)
        await decks_list(callback.message, state)


@router.callback_query(F.data == 'edit_card')
@router.callback_query(F.data == 'delete_card')
@check_current_state
async def card_update_delete_begin(callback: CallbackQuery, state: FSMContext):
    operation = callback.data
    if operation == 'edit_card':
        text = '🔢 Enter the card number from the list:'
    else:
        text = '🔢 Enter one card number or several cards numbers from the list:'
    await callback.answer()
    await state.set_state(CardManage.upd_list_index if callback.data == 'edit_card' else CardManage.del_list_index)
    await callback.message.answer(text, reply_markup=ReplyKeyboardRemove())


async def delete_cards(card_id, slug):
    deleted_cards_count = 0
    url = f'{BASE_URL}/cards/api/v1/manage/{card_id}/'
    response = await send_request(url, method='DELETE', data={'slug': slug})
    status = response.get('status')
    if status == 204:
        deleted_cards_count += 1
    return deleted_cards_count


@router.message(CardManage.del_list_index)
async def card_delete_getting_id(message: Message, state: FSMContext):
    index = message.text
    if len(index) > 50:
        text = '❕️ Message must contain maximum 50 chars.'
        return await display_message_and_redirect(message, state, text)

    index_split = [j.split('.') for i in index.split(',') for j in i.split(' ')]
    index_merging = list(chain(*index_split))
    index_integers = set([int(num) for char in index if (num := char.strip()).isdigit()])

    if len(index_integers) == 0:
        text = '❕️ Index must be an integer. Try again.'
        return await display_message_and_redirect(message, state, text)

    data = await state.get_data()
    slug = data.get('slug')
    cards_id_index = data.get('cards_id_index')
    cards_id_list = [card_id for num in index_integers if (card_id := cards_id_index.get(num))]

    if not slug and not isinstance(cards_id_index, dict):
        text = '❗️ Please try again.'
    elif not cards_id_list:
        text = '❗️ Index must be in the list of cards. Try again.'

    if 'text' in locals():
        return await display_message_and_redirect(message, state, text)

    current_state = await state.get_state()

    deleted_cards_count = await asyncio.gather(*[delete_cards(card_id, slug) for card_id in cards_id_list])
    if deleted_cards_count != 0:
        text = f'💣 Successfully deleted {sum(deleted_cards_count)} cards.'
    else:
        text = f'❗️ Something went wrong.'
    await message.answer(text, reply_markup=await kb.back_to_decklist_or_deckdetails(slug))
    # await display_message_and_redirect(message, state, text)


@router.message(CardManage.upd_list_index)
async def card_update_getting_id(message: Message, state: FSMContext):
    index = message.text

    if not index.isdigit():
        text = '️️❕️ Index must be an integer. Try again.'
        return await display_message_and_redirect(message, state, text)

    index = int(index)
    data = await state.get_data()
    slug = data.get('slug')
    cards_id_index = data.get('cards_id_index')

    if not slug or not isinstance(cards_id_index, dict):
        text = '🧸 Please try again.'
    elif index not in cards_id_index:
        text = '❕️ Index must be in the list of cards. Try again.'

    if 'text' in locals():
        return await display_message_and_redirect(message, state, text)

    card_id = cards_id_index.get(index, 0)
    await state.update_data(card_ops_state='upd', card_id=card_id)
    await state.set_state(CardManage.front_side)
    await message.answer('☝️ Enter front side:')


@router.message(CardManage.front_side)
@router.message(CardManage.back_side)
async def card_update_create_enter_sides(message: Message, state: FSMContext):
    start_time = time.time()

    side = message.text.strip()

    if len(side) > 255:
        text = '⛔️ Side must be a maximum of 255 characters.'
    elif not any(char.isalnum() for char in side):
        text = '⛔️ Side must contain one letter or one number.'
    if 'text' in locals():
        await message.answer(text, reply_markup=kb.studying_start)
        await asyncio.sleep(1.5)
        await decks_list(message, state)
        print('Mistake', time.time() - start_time)

        return

    side = side.capitalize()
    current_state = await state.get_state()
    data, next_state, text, keyboard = {}, None, '', None

    if current_state == 'CardManage:front_side':
        data = {'front_side': side}
        next_state = CardManage.back_side
        text = '✌️ Enter back side'
        keyboard = ReplyKeyboardRemove()
    elif current_state == 'CardManage:back_side':
        data = {'back_side': side}
        next_state = CardManage.is_two_sides
        text = 'Would you like to study the two sides?'
        keyboard = await kb.is_two_sides()

    await state.update_data(data)
    await state.set_state(next_state)
    await message.answer(text, reply_markup=keyboard)
    print('Success', time.time() - start_time)


#

@router.callback_query(F.data.in_(('is_two_sides', 'is_one_side')))
@check_current_state
async def card_update_create_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    choice = True if callback.data == 'is_two_sides' else False
    data = await state.get_data()
    operation = data.get('card_ops_state')
    if operation == 'create':
        method = 'POST'
        text = '🎉 Card successfully created.'
        url = f'{BASE_URL}/cards/api/v1/manage/'
    else:
        method = 'PUT'
        text = '🪅 Card successfully updated.'
        card_id = data.get('card_id')
        url = f'{BASE_URL}/cards/api/v1/manage/{card_id}/'

    card_data = {
        'side1': (side1 := data.get('front_side')),
        'side2': data.get('back_side'),
        'slug': (slug := data.get('slug')),
        'is_two_sides': choice,
    }

    response = await send_request(url, method=method, data=card_data)
    status = response.get('status')
    if status // 100 == 2:
        keyboard = await kb.card_create_upd_finish(slug, is_create=True if operation == 'create' else False)
        await callback.message.delete()
        await state.clear()
        await state.set_state(CardManage.card_ops_state)
        await callback.message.answer(f'🎊  {text}  🎊', reply_markup=keyboard)
    else:
        text = '❕️ Something went wrong. Please try again.'
        return await display_message_and_redirect(callback.message, state, text)
