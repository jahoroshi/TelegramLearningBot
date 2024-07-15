import asyncio

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.methods import SetChatMenuButton
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, BotCommand, MenuButtonCommands, \
    BotCommandScopeDefault, BotCommandScopeChat
from bot import bot
import app.keyboards as kb
from app.handlers import card_mode_start
from app.requests import send_request
from app.services import generate_deck_list_text, check_current_state, display_message_and_redirect
from settings import BASE_URL

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


router = Router()


class DeckRename(StatesGroup):
    new_name = State()


class DeckDelete(StatesGroup):
    active = State()


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
    response = await send_request(get_decks_url)
    if response.get('status') // 100 == 2:
        await state.set_state(DeckViewingState.active)
        await message.answer(f'🗃 *{f"__Decks__":^50}* 🗃', parse_mode=ParseMode.MARKDOWN_V2,
                             reply_markup=await kb.deckhub_manage_button())
        for deck in response.get('data'):
            text = await generate_deck_list_text(deck)
            await message.answer(text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=await kb.decks_list(deck))
    else:
        await message.answer('Something went wrong. Please press REFRESH button.', reply_markup=kb.refresh_session)


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
@check_current_state
async def manage_deck(callback: CallbackQuery, state: FSMContext):
    slug = callback.data.split('_')[-1]
    await callback.message.edit_reply_markup(reply_markup=await kb.manage_deck(slug))


@router.callback_query(F.data.startswith('rename_deck_'))
@check_current_state
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
    if len(new_name) > 100:
        text = '❕️ New name must contain maximum 100 chars.'
        return await display_message_and_redirect(message, state, text)

    if new_name and any(char.isalnum() for char in new_name):
        new_name = new_name.capitalize().strip()
        slug = data.get('slug')
        url = f'{BASE_URL}/deck/api/v1/manage/{slug}/'
        response = await send_request(url, method='PUT', data={'name': new_name})
        status = response.get('status', 0)
        if status // 100 == 2:
            text = 'Deck name was successfully changed.'
        else:
            text = 'Something went wrong.'
    else:
        text = 'Name must consist of letters or numbers. Please try again.'
    await display_message_and_redirect(message, state, text)


@router.callback_query(F.data.startswith('delete_deck_'))
@check_current_state
async def confirm_delete_deck(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(DeckDelete.active)
    slug = callback.data.split('_')[-1]
    text = 'Are you sure to delete this deck?'
    await callback.message.answer(text, reply_markup=await kb.confirm_delete_desk(slug))


@router.callback_query(F.data.startswith('confirm_delete_deck_'))
async def deck_delete(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state == DeckDelete.active:
        slug = callback.data.split('_')[-1]
        url = f'{BASE_URL}/deck/api/v1/manage/{slug}/'
        response = await send_request(url, method='DELETE')
        if response.get('status') == 204:
            text = '🧨 Deck was successfully deleted.'
            await callback.message.delete()
        else:
            text = 'Something went wrong.'
            await callback.message.delete_reply_markup()
        await callback.message.answer(text, reply_markup=kb.studying_start)
        await asyncio.sleep(1.5)
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

# @router.callback_query(F.data == 'deckhub_manage')
# async def deckhub_manage(callback: CallbackQuery, state: FSMContext):
#     await callback.message.edit_reply_markup()


@router.message(F.text == 'b')
async def send_welcome(message: types.Message):
    user_commands = [
        BotCommand(command='for', description='Описание команды /for'),
        BotCommand(command='for2', description='Описание команды /for2'),
        BotCommand(command='magik', description='Описание команды /magik'),
        BotCommand(command='magik22', description='Описание команды /magik'),
        BotCommand(command='magik2ww2', description='Описание команды /magik'),
    ]

    # Предполагаем, что у вас используется aiogram
    menu_button = MenuButtonCommands(commands=user_commands)

    res = await bot.set_my_commands(user_commands, scope=BotCommandScopeChat(chat_id=message.chat.id))
    # await bot(SetChatMenuButton(menu_button=menu_button))

# @router.message(F.text == 'a')
# async def send_welcome(message: types.Message):
#
#     web_app_info = types.WebAppInfo(url="https://chatgpt.com/")
#     menu_button = types.MenuButtonWebApp(text="Open Web App", web_app=web_app_info)
#     await bot.set_chat_menu_button(chat_id=message.chat.id, menu_button=menu_button)
#     await message.answer("Web app menu button has been set.")