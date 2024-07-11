import asyncio
import functools

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

import app.keyboards as kb
from app.handlers import to_decks_list, decks_list
from app.requests import send_request
from settings import BASE_URL

router = Router()

class ImportCards(StatesGroup):
    data = State()


class CardManage(StatesGroup):
    card_ops_state = State()
    upd_list_index = State()
    del_list_index = State()
    front_side = State()
    back_side = State()
    is_two_sides = State()


def check_current_state(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        state = kwargs.get('state')
        current_state = await state.get_state()
        if current_state in ('DeckViewingState:active', 'CardManage:card_ops_state', 'CardManage:is_two_sides'):
            return await func(*args, **kwargs)
        else:
            print(current_state)
            print(kwargs)
            return await to_decks_list(*args, **kwargs)
    return wrapper


@router.callback_query(F.data.startswith('import_cards_'))
@check_current_state
async def import_cards(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(ImportCards.data)
    slug = callback.data.split('_')[-1]
    await state.update_data(slug=slug)
    await callback.message.answer(
        f'''*Import instruction:*
» Max lenght message 4096 chars\.\n
» Use semicolon * \; * as separator between sides\n
» Each card must be on a new line\.

*Example\:*
>\(_front side_\) *\;* \(_back side_\)
>{f"Apple":^14} *\;* {f"Яблоко":^11}
>{f"Orange":^12} *\;* {f"Апельсин":^11}

_enter text or press back for cansel_
''', parse_mode=ParseMode.MARKDOWN_V2, reply_markup=await kb.back())


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
    request = await send_request(url, method='POST', data=cards_data)
    if isinstance(request, dict):
        text = request.get('detail')
    else:
        text = 'Something went wrong.'
    await message.answer(text, reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(1)
    await decks_list(message, state)




@router.callback_query(F.data.startswith('add_card_'))
@check_current_state
async def card_create_begin(callback: CallbackQuery, state: FSMContext):
    slug = callback.data.split('_')[-1]
    await state.set_state(CardManage.front_side)
    await state.update_data(card_ops_state='create')
    await state.update_data(slug=slug)
    await callback.message.edit_reply_markup(reply_markup=await kb.back())
    await callback.message.answer('Enter front side\n>Or press    *back*   for cansel',
                                  parse_mode=ParseMode.MARKDOWN_V2, reply_markup=ReplyKeyboardRemove())



@router.callback_query(F.data.startswith('show_cards_'))
@check_current_state
async def show_cards(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    slug = callback.data.split('_')[-1]
    tg_id = state.key.user_id
    url = f'{BASE_URL}/deck/api/v1/manage/{tg_id}/{slug}/'
    request = await send_request(url, method='GET')
    if isinstance(request, list) and isinstance(request[0], dict):
        cards_id_index = {}
        cards_list = ''
        for index, card in enumerate(request, 1):
            cards_id_index[index] = card.get('id')
            cards_list += f'» {index}. {card.get("side1")} ¦ {card.get("side2")}\n'
        if len(cards_list) != 0:
            await callback.message.answer(cards_list, reply_markup=await kb.show_cards_action_buttons(slug))
            await state.set_state(CardManage.card_ops_state)
            await state.update_data(cards_id_index=cards_id_index, slug=slug)
        else:
            await callback.message.answer('The deck is empty.')
            await asyncio.sleep(1.5)
            await decks_list(callback.message, state)

    else:
        text = 'Something went wrong.'
        await callback.message.answer(text, reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(1.5)
        await decks_list(callback.message, state)


@router.callback_query(F.data == 'edit_card')
@router.callback_query(F.data == 'delete_card')
@check_current_state
async def card_update_delete_begin(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(CardManage.upd_list_index if callback.data == 'edit_card' else CardManage.del_list_index)
    await callback.message.answer('⌨️ Enter the card number from the list:', reply_markup=ReplyKeyboardRemove())

@router.message(CardManage.del_list_index)
@router.message(CardManage.upd_list_index)
async def card_update_delete_handler(message: Message, state: FSMContext):
    index = message.text
    if index.isdigit():
        index = int(index)
        data = await state.get_data()
        slug = data.get('slug')
        cards_id_index = data.get('cards_id_index')
        if slug and isinstance(cards_id_index, dict):
            if index in cards_id_index:
                current_state = await state.get_state()
                if current_state == 'CardManage:upd_list_index':
                    await state.update_data(card_ops_state='upd', card_id=cards_id_index.get(index, 0))
                    await state.set_state(CardManage.front_side)
                    await message.answer('☝️ Enter front side:')
                    return
                else:
                    url = f'{BASE_URL}/cards/api/v1/manage/{cards_id_index.get(index, 0)}'
                    request = await send_request(url, method='DELETE', data={'slug': slug})
                    if request == 204:
                        text = 'Card was successfully deleted.'
                    else:
                        text = 'Something went wrong.'
            else:
                text = 'Index must be in the list of cards. Try again.'
        else:
            text = 'Please try again.'
    else:
        text = 'Index must be an integer. Try again.'

    await message.answer(text, reply_markup=kb.studying_start)
    await asyncio.sleep(1.5)
    await decks_list(message, state)


@router.message(CardManage.front_side)
@router.message(CardManage.back_side)
async def card_update_create_enter_sides(message: Message, state: FSMContext):
    side = message.text.strip()

    if len(side) > 255:
        text = 'Side must be a maximum of 255 characters.'
    elif not any(char.isalnum() for char in side):
        text = 'Side must contain one letter or one number.'
    if 'text' in locals():
        await message.answer(text, reply_markup=kb.studying_start)
        await asyncio.sleep(1.5)
        await decks_list(message, state)
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


@router.callback_query(F.data.in_(('is_two_sides', 'is_one_side')))
@check_current_state
async def card_update_create_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    choice = True if callback.data == 'is_two_sides' else False
    data = await state.get_data()
    operation = data.get('card_ops_state')
    if operation == 'create':
        method = 'POST'
        text = 'Card successfully created.'
        url = f'{BASE_URL}/cards/api/v1/manage/'
    else:
        method = 'PUT'
        text = 'Card successfully updated.'
        card_id = data.get('card_id')
        url = f'{BASE_URL}/cards/api/v1/manage/{card_id}/'

    card_data = {
        'side1': (side1 := data.get('front_side')),
        'side2': data.get('back_side'),
        'slug': (slug := data.get('slug')),
        'is_two_sides': choice,
    }

    request = await send_request(url, method=method, data=card_data)
    if request and request.get('side1') == side1:
        keyboard = await kb.card_manage_end(slug if operation == 'create' else None)
        await state.clear()
        await state.set_state(CardManage.card_ops_state)
        await callback.message.answer(f'🎊  {text}  🎊', reply_markup=keyboard)
