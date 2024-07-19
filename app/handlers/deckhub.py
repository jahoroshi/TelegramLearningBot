import asyncio

from aiogram import F, Router
from aiogram import types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, BotCommand, MenuButtonCommands, \
    BotCommandScopeChat

import app.keyboards as kb
from app.handlers import card_mode_start
from app.requests import send_request
from app.services import check_current_state, display_message_and_redirect, generate_deck_list, clear_current_state, \
    DeckViewingState, DeckRename, DeckDelete, DeckCreate
from bot import bot
from settings import BASE_URL

router = Router()





@router.message(F.text.in_(('Decks', 'Back to desks list')))
@router.message(Command('back'))
async def decks_list(message: Message, state: FSMContext, caller=None):
    tg_id = state.key.user_id if state else message.from_user.id
    get_decks_url = f'{BASE_URL}/deck/api/v1/manage/{tg_id}/'
    response = await send_request(get_decks_url)
    if response.get('status') // 100 == 2:
        await state.set_state(DeckViewingState.active)
        text = 'Choose a deck from the list below:'
        params = {
            'parse_mode': ParseMode.MARKDOWN_V2,
            'reply_markup': await kb.deck_names(response.get('data')),
        }
        if caller == 'from back btn':
            await message.edit_text(text, **params)
        else:
            await message.answer(f'🗃 *{f"__Decks__":^50}* 🗃', parse_mode=ParseMode.MARKDOWN_V2,
                                 reply_markup=kb.refresh_session)
            await message.answer(text, **params)

        # await message.answer(text, parse_mode=ParseMode.MARKDOWN_V2,
        #                      reply_markup=await kb.deck_names(response.get('data')))
    else:
        await message.answer('Something went wrong. Please press REFRESH button.', reply_markup=kb.refresh_session)


@router.callback_query(F.data.startswith('deck_details_'))
@clear_current_state
async def deck_details(callback_or_message: CallbackQuery or Message, state: FSMContext, slug=None):
    if isinstance(callback_or_message, CallbackQuery):
        message = callback_or_message.message
        slug = callback_or_message.data.split('_')[-1]
    else:
        message = callback_or_message
    url = f'{BASE_URL}/deck/api/v1/manage/{slug}/'
    response = await send_request(url)
    if response.get('status') == 200:
        data = response.get('data')
        text = await generate_deck_list(data)
        await message.edit_text(text, parse_mode=ParseMode.MARKDOWN_V2,
                                        reply_markup=await kb.manage_deck(data))


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

@router.callback_query(F.data == 'to_decks_list')
async def to_decks_list(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await decks_list(callback.message, state)


@router.callback_query(F.data == 'back_to_decks')
async def back_to_decks_btn(callback: CallbackQuery, state: FSMContext):
    # await state.clear()
    await callback.answer()
    await decks_list(callback.message, state, caller='from back btn')


@router.callback_query(F.data.startswith('start_studying_'))
async def launch_card_mode(callback: CallbackQuery, state: FSMContext):
    slug, study_mode = callback.data.split('_')[-2:]
    await state.clear()
    await card_mode_start(callback.message, state, slug=slug, study_mode=study_mode)


# @router.callback_query(F.data.startswith('manage_deck_'))
# @check_current_state
# async def manage_deck(callback: CallbackQuery, state: FSMContext):
#     slug = callback.data.split('_')[-1]
#     await callback.message.edit_reply_markup(reply_markup=await kb.manage_deck(slug))


@router.callback_query(F.data.startswith('rename_deck_'))
@check_current_state
async def rename_deck(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    slug = callback.data.split('_')[-1]
    await state.set_state(DeckRename.new_name)
    await state.update_data(slug=slug)
    # await callback.message.edit_reply_markup(reply_markup=await kb.back())
    await callback.message.answer('*Enter new deck\'s name*\n>Or press    *\/back*    for cansel',
                                  parse_mode=ParseMode.MARKDOWN_V2)


@router.message(DeckRename.new_name)
async def rename_deck_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    new_name = message.text
    if len(new_name) > 100:
        text = '❕️ New name must contain maximum 100 chars.'
        return await message.answer(text)
        # return await display_message_and_redirect(message, state, text)

    if new_name and any(char.isalnum() for char in new_name):
        new_name = new_name.capitalize().strip()
        slug = data.get('slug')
        url = f'{BASE_URL}/deck/api/v1/manage/{slug}/'
        response = await send_request(url, method='PUT', data={'name': new_name})
        status = response.get('status', 0)
        if status // 100 == 2:
            text = 'Deck name was successfully changed.'
            slug = response.get('data', {}).get('slug')
        else:
            text = 'Something went wrong.'
        await state.set_state(DeckViewingState.active)
        await message.answer(text, reply_markup=await kb.back_to_decklist_or_deckdetails(slug))
    else:
        text = 'Name must consist of letters or numbers. Please try again.'
        await message.answer(text)
    # await deck_info(message, state, slug)
    # await display_message_and_redirect(message, state, text)


@router.callback_query(F.data.startswith('delete_deck_'))
@check_current_state
async def delete_deck_confirm(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(DeckDelete.active)
    slug = callback.data.split('_')[-1]
    text = 'Are you sure to delete this deck?'
    await callback.message.delete_reply_markup()
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
        await state.set_state(DeckViewingState.active)
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

@router.message(Command(commands=['newdeck']))
async def deck_create(message: Message, state: FSMContext):
    text = 'Enter new deck\'s name'
    await message.answer(text, reply_markup=await kb.back())
    await state.set_state(DeckCreate.name)


@router.message(DeckCreate.name)
async def deck_create_handler(message: Message, state: FSMContext):
    name = message.text
    telegram_id = state.key.user_id
    data = {
        'name': name,
        'telegram_id': telegram_id,
    }
    url = f'{BASE_URL}/deck/api/v1/manage/'
    response = await send_request(url, method='POST', data=data)

    if response.get('status') == 201:
        text = '🎉 Deck was successfully created.'
    else:
        text = 'Something went wrong.'
    await display_message_and_redirect(message, state, text)


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
