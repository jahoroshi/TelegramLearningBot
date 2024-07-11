import asyncio

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

import app.keyboards as kb
from app.handlers import card_mode_start
from app.requests import send_request
from app.services import generate_deck_list_text
from settings import BASE_URL

router = Router()


class DeckRename(StatesGroup):
    new_name = State()


class ImportCards(StatesGroup):
    data = State()

class DeckViewingState(StatesGroup):
    active = State()

class CardManage(StatesGroup):
    card_ops_state = State()
    upd_list_index = State()
    del_list_index = State()
    front_side = State()
    back_side = State()
    is_two_sides = State()



@router.message(F.text.in_(('Decks', 'Back to desks list')))
@router.message(Command('to_desks_list'))
async def decks_list(message: Message, state: FSMContext):
    tg_id = state.key.user_id
    get_decks_url = f'{BASE_URL}/deck/api/v1/manage/{tg_id}/'
    decks_data = await send_request(get_decks_url)
    if decks_data:
        await state.set_state(DeckViewingState.active)
        await message.answer(f'🗃 *{f"__Decks__":^50}* 🗃', parse_mode=ParseMode.MARKDOWN_V2)
        for deck in decks_data:
            text = await generate_deck_list_text(deck)
            await message.answer(text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=await kb.decks_list(deck))


@router.callback_query(F.data == 'to_decks_list')
async def to_decks_list(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await decks_list(callback.message, state)
    await callback.answer()


@router.callback_query(F.data.startswith('start_studying_'))
async def launch_card_mode(callback: CallbackQuery, state: FSMContext):
    slug, study_mode = callback.data.split('_')[-2:]
    await state.clear()
    await card_mode_start(callback.message, state, slug=slug, study_mode=study_mode)


@router.callback_query(F.data.startswith('manage_deck_'))
async def manage_deck(callback: CallbackQuery, state: FSMContext):
    slug = callback.data.split('_')[-1]
    await callback.message.edit_reply_markup(reply_markup=await kb.manage_deck(slug))


@router.callback_query(F.data.startswith('rename_deck_'))
async def rename_deck(callback: CallbackQuery, state: FSMContext):
    slug = callback.data.split('_')[-1]
    await state.set_state(DeckRename.new_name)
    await state.update_data(slug=slug)
    await callback.message.edit_reply_markup(reply_markup=await kb.back())
    await callback.message.answer('*Enter new deck\'s name*\n>Or press    *back*    for cansel',
                                  parse_mode=ParseMode.MARKDOWN_V2,
                                  reply_markup=ReplyKeyboardRemove())


@router.message(DeckRename.new_name)
async def rename_deck_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    new_name = message.text
    if new_name and new_name.isalnum():
        new_name = new_name.capitalize().strip()
        slug = data.get('slug')
        url = f'{BASE_URL}/deck/api/v1/manage/{slug}/'
        request = await send_request(url, method='PUT', data={'name': new_name})
        if request and request.get('name', '').capitalize() == new_name:
            await message.reply('Deck name was successfully changed.')
            await asyncio.sleep(1)
        await state.clear()
        await decks_list(message, state)
    else:
        await message.answer('Name must consist of letters or numbers. Please try again.')
        await asyncio.sleep(2)
        await state.clear()
        await decks_list(message, state)


@router.callback_query(F.data.startswith('delete_deck_'))
async def deck_delete(callback: CallbackQuery, state: FSMContext):
    slug = callback.data.split('_')[-1]
    url = f'{BASE_URL}/deck/api/v1/manage/{slug}/'
    request = await send_request(url, method='DELETE')
    if request == 204:
        text = 'Deck was successfully deleted.'
    else:
        text = 'Something went wrong.'
    await callback.answer()
    await callback.message.answer(text, reply_markup=kb.studying_start)
    await asyncio.sleep(1)
    await decks_list(callback.message, state)


# @router.message(AddCard.front_side)
# @router.message(AddCard.back_side)
# async def add_card_sides(message: Message, state: FSMContext):
#     side = message.text
#     if side and any(char.isalnum() for char in side):
#         side = side.capitalize().strip()
#         current_state = await state.get_state()
#         if current_state == 'AddCard:front_side':
#             await state.set_state(AddCard.back_side)
#             await state.update_data(front_side=side)
#             await message.answer('Enter back side', reply_markup=ReplyKeyboardRemove())
#         elif current_state == 'AddCard:back_side':
#             await state.set_state(AddCard.is_two_sides)
#             await state.update_data(back_side=side)
#             await message.answer('Would you like to study the two sides?', reply_markup=await kb.is_two_sides())
#     else:
#         await message.answer('Side must consist of letters or numbers. Please try again.')
#         await asyncio.sleep(2)
#         await state.clear()
#         await decks_list(message, state)

