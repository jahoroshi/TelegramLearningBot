import asyncio
from itertools import chain

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.handlers import decks_list
from app.requests import send_request
from app.utils import check_current_state, display_message_and_redirect, CardManage, get_decks_data
from app.middlewares.i18n_init import i18n
from settings import BASE_URL

router = Router()
router_quick_card_create = Router()

_ = i18n.gettext


@router_quick_card_create.message()
async def quick_card_create_begin(message: Message, state: FSMContext):
    side1 = message.text
    if 2 <= len(side1) <= 255 and any(char.isalpha() for char in side1):
        await state.set_state(CardManage.back_side)
        await state.update_data(card_ops_state='create', front_side=side1)


@router.message(Command(commands=['addcard']))
async def command_card_create_begin(message: Message, state: FSMContext):
    await state.set_state(CardManage.front_side)
    await state.update_data(card_ops_state='create')
    await message.answer(_('enter_front_side'), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=await kb.back())


@router.callback_query(F.data.startswith('add_card_'))
@check_current_state
async def card_create_begin(callback: CallbackQuery, state: FSMContext):
    slug = callback.data.split('_')[-1]
    await state.set_state(CardManage.front_side)
    await state.update_data(card_ops_state='create')
    await state.update_data(slug=slug)
    await callback.message.edit_reply_markup(reply_markup=await kb.back_to_decklist_or_deckdetails(slug))
    await callback.message.answer(_('enter_front_side'), parse_mode=ParseMode.MARKDOWN_V2)


@router.callback_query(F.data == 'edit_card')
@router.callback_query(F.data == 'delete_card')
@check_current_state
async def card_update_delete_begin(callback: CallbackQuery, state: FSMContext):
    operation = callback.data
    if operation == 'edit_card':
        text = _('enter_card_number_edit')
    else:
        text = _('enter_card_number_delete')
    await callback.answer()
    await state.set_state(CardManage.upd_list_index if callback.data == 'edit_card' else CardManage.del_list_index)
    await callback.message.answer(text)


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
        text = _('max_50_chars')
        return await display_message_and_redirect(message, state, text)

    index_split = [j.split('.') for i in index.split(',') for j in i.split(' ')]
    index_merging = list(chain(*index_split))
    index_integers = set([int(num) for char in index if (num := char.strip()).isdigit()])

    if len(index_integers) == 0:
        text = _('index_integer_try_again')
        return await display_message_and_redirect(message, state, text)

    data = await state.get_data()
    slug = data.get('slug')
    cards_id_index = data.get('cards_id_index')
    cards_id_list = [card_id for num in index_integers if (card_id := cards_id_index.get(num))]

    if not slug and not isinstance(cards_id_index, dict):
        text = _('please_try_again')
    elif not cards_id_list:
        text = _('index_must_be_in_list')

    if 'text' in locals():
        return await display_message_and_redirect(message, state, text)

    current_state = await state.get_state()

    deleted_cards_count = await asyncio.gather(*[delete_cards(card_id, slug) for card_id in cards_id_list])
    if deleted_cards_count != 0:
        text = _('successfully_deleted_cards').format(sum(deleted_cards_count))
    else:
        text = _('something_went_wrong')
    await message.answer(text, reply_markup=await kb.back_to_decklist_or_deckdetails(slug))


@router.message(CardManage.upd_list_index)
async def card_update_getting_id(message: Message, state: FSMContext):
    index = message.text

    if not index.isdigit():
        text = _('index_must_be_digit')
        return await display_message_and_redirect(message, state, text)

    index = int(index)
    data = await state.get_data()
    slug = data.get('slug')
    cards_id_index = data.get('cards_id_index')

    if not slug or not isinstance(cards_id_index, dict):
        text = _('please_try_again_emoji')
    elif index not in cards_id_index:
        text = _('index_must_be_in_list')

    if 'text' in locals():
        return await display_message_and_redirect(message, state, text)

    card_id = cards_id_index.get(index, 0)
    await state.update_data(card_ops_state='upd', card_id=card_id)
    await state.set_state(CardManage.front_side)
    await message.answer(_('enter_front_side_no_emoji'))


async def check_sides_input(message: Message, state: FSMContext, side: str):
    if side == '...':
        return True
    if len(side) > 255:
        text = _('max_255_chars')
    elif not any(char.isalnum() for char in side):
        text = _('side_must_contain_alnum')
    if 'text' in locals():
        await message.answer(text, reply_markup=kb.refresh_button)
        await asyncio.sleep(1.5)
        await decks_list(message, state)
        return False
    return True


async def handle_sides(state: FSMContext, side):
    current_state = await state.get_state()
    if current_state == 'CardManage:front_side':
        data = {'front_side': side}
        next_state = CardManage.back_side
        text = _('enter_back_side')
        keyboard = None
    else:
        data = {'back_side': side}
        next_state = CardManage.is_two_sides
        text = _('study_two_sides')
        keyboard = await kb.is_two_sides()
    return data, next_state, text, keyboard


@router.message(CardManage.front_side)
@router.message(CardManage.back_side)
async def card_update_create_enter_sides(message: Message, state: FSMContext, side1: str = None):
    side = message.text.strip() if not side1 else side1
    if await check_sides_input(message, state, side) is False:
        return

    side = side.capitalize()
    data, next_state, text, keyboard = await handle_sides(state, side)

    await state.update_data(data)
    await state.set_state(next_state)
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith(('is_two_sides', 'is_one_side', 'addcard_slug_')))
@check_current_state
async def card_update_create_handler(callback: CallbackQuery, state: FSMContext, card_data=None):
    data = await state.get_data()
    if callback.data.startswith('addcard_slug_'):
        slug = callback.data.split('_')[-1]
    else:
        slug = data.get('slug')

    if slug:
        await callback.answer()
        message = callback.message
        operation = data.get('card_ops_state')
    else:
        await card_create_get_slug(callback.message, state)
        is_two_sides = True if callback.data == 'is_two_sides' else False
        await state.update_data(is_two_sides=is_two_sides)
        return

    is_two_sides = True if callback.data == 'is_two_sides' or data.get('is_two_sides') else False

    if operation == 'create':
        method = 'POST'
        text = _('card_created')
        url = f'{BASE_URL}/cards/api/v1/manage/'
    else:
        method = 'PUT'
        text = _('card_updated')
        card_id = data.get('card_id')
        url = f'{BASE_URL}/cards/api/v1/manage/{card_id}/'

    side1 = data.get('front_side')
    side2 = data.get('back_side')

    card_data = {
        'side1': side1 if side1 != '...' else None,
        'side2': side2 if side2 != '...' else None,
        'slug': slug,
        'is_two_sides': is_two_sides,
    }

    card_data = {k: v for k, v in card_data.items() if v is not None}

    response = await send_request(url, method=method, data=card_data)
    status = response.get('status')
    if status // 100 == 2:
        keyboard = await kb.card_create_upd_finish(slug, is_create=True if operation == 'create' else False)
        await state.clear()
        await state.set_state(CardManage.card_ops_state)
        await message.edit_text(_('success_message').format(text), reply_markup=keyboard)
    else:
        text = _('something_went_wrong')
        return await display_message_and_redirect(message, state, text)


async def card_create_get_slug(message: Message, state: FSMContext):
    decks_data, status = await get_decks_data(message, state)
    if status == 200:
        text = _('choose_deck')
        params = {
            'parse_mode': ParseMode.MARKDOWN_V2,
            'reply_markup': await kb.deck_names(decks_data, is_quick_add=True),
        }
        await state.set_state(CardManage.addcard_slug)
    else:
        text = _('oops_something_went_wrong')
        params = {'parse_mode': ParseMode.HTML, 'reply_markup': await kb.back()}

    await message.edit_text(text, **params)
