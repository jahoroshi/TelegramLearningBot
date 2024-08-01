import asyncio

from aiogram import F, Router
from aiogram import types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, BotCommand, MenuButtonCommands, \
    BotCommandScopeChat, ReplyKeyboardRemove

import app.keyboards as kb
from app.handlers.cardmode.cardmode_start import card_mode_start
from app.requests import send_request
from app.middlewares.locales import i18n
from app.services import check_current_state, display_message_and_redirect, create_deck_info, clear_current_state, \
    DeckViewingState, DeckRename, DeckDelete, DeckCreate, delete_two_messages, get_decks_data
from app.services.states import ServerError, ResetDeckProgress
from bot import bot
from settings import BASE_URL

_ = i18n.gettext
router = Router()










# @router.message(F.text.in_(('Decks', 'Back to desks list')))
# @router.message(Command('to_desks_list'))
# async def decks_list(message: Message, state: FSMContext):
#     tg_id = state.key.user_id
#     get_decks_url = f'{BASE_URL}/deck/api/v1/manage/{tg_id}/'
#     response = await send_request(get_decks_url)
#     if response.get('status') // 100 == 2:
#         await state.set_state(DeckViewingState.active)
#         await message.answer(f'🗃 *{f"__Decks__":^50}* 🗃', parse_mode=ParseMode.MARKDOWN_V2,
#                              reply_markup=await kb.deckhub_manage_button())
#         for deck in response.get('data'):
#             text = await generate_deck_list_text(deck)
#             await message.answer(text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=await kb.decks_list(deck))
#     else:
#         await message.answer('Something went wrong. Please press REFRESH button.', reply_markup=kb.refresh_session)
#












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





