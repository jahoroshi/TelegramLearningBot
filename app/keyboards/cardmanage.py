from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def show_cards_action_buttons(slug):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Add card', callback_data=f'add_card_{slug}'))
    keyboard.add(InlineKeyboardButton(text='Edit card', callback_data='edit_card'))
    keyboard.add(InlineKeyboardButton(text='Delete card', callback_data='delete_card'))
    keyboard.add(InlineKeyboardButton(text='« Back to decks list', callback_data='back_to_decks'))
    keyboard.add(InlineKeyboardButton(text='« Back to deck', callback_data=f'deck_details_{slug}'))
    return keyboard.adjust(3, 2).as_markup()


async def is_two_sides():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Yes', callback_data='is_two_sides'))
    keyboard.add(InlineKeyboardButton(text='No', callback_data='is_one_side'))
    return keyboard.as_markup()


async def card_create_upd_finish(slug, is_create=None):
    keyboard = InlineKeyboardBuilder()
    if is_create:
        keyboard.add(InlineKeyboardButton(text='Add another card', callback_data=f'add_card_{slug}'))

    keyboard.add(InlineKeyboardButton(text='« Back to decks list', callback_data='back_to_decks'))
    keyboard.add(InlineKeyboardButton(text='« Back to deck', callback_data=f'deck_details_{slug}'))
    return keyboard.adjust(1, 2).as_markup()


# async def back_to_cardmanage(slug):
#     keyboard = InlineKeyboardBuilder()
#     keyboard.add(InlineKeyboardButton(text='Back to deck manage', callback_data='to_decks_list'))