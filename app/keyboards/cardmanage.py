from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def show_cards_action_buttons(slug):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Add new card', callback_data=f'add_card_{slug}'))
    keyboard.add(InlineKeyboardButton(text='Edit card', callback_data='edit_card'))
    keyboard.add(InlineKeyboardButton(text='Delete card', callback_data='delete_card'))
    keyboard.add(InlineKeyboardButton(text='Back', callback_data='to_decks_list'))
    return keyboard.adjust(2, 2).as_markup()


async def is_two_sides():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Yes', callback_data='is_two_sides'))
    keyboard.add(InlineKeyboardButton(text='No', callback_data='is_one_side'))
    return keyboard.as_markup()


async def card_manage_end(slug=None):
    keyboard = InlineKeyboardBuilder()
    if slug:
        keyboard.add(InlineKeyboardButton(text='Add another card', callback_data=f'add_card_{slug}'))
    keyboard.add(InlineKeyboardButton(text='Back', callback_data='to_decks_list'))
    return keyboard.adjust(1).as_markup()
