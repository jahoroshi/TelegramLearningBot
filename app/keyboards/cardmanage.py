from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.middlewares.i18n_init import i18n

_ = i18n.gettext


async def show_cards_action_buttons(slug):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('add_card'), callback_data=f'add_card_{slug}'))
    keyboard.add(InlineKeyboardButton(text=_('edit_card'), callback_data='edit_card'))
    keyboard.add(InlineKeyboardButton(text=_('delete_card'), callback_data='delete_card'))
    keyboard.add(InlineKeyboardButton(text=_('back_to_decks_list'), callback_data='back_to_decks'))
    keyboard.add(InlineKeyboardButton(text=_('back_to_deck'), callback_data=f'deck_details_{slug}'))
    return keyboard.adjust(3, 2).as_markup()


async def is_two_sides():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('yes'), callback_data='is_two_sides'))
    keyboard.add(InlineKeyboardButton(text=_('no'), callback_data='is_one_side'))
    return keyboard.as_markup()


async def card_create_upd_finish(slug, is_create=None):
    keyboard = InlineKeyboardBuilder()
    if is_create:
        keyboard.add(InlineKeyboardButton(text=_('add_another_card'), callback_data=f'add_card_{slug}'))

    keyboard.add(InlineKeyboardButton(text=_('back_to_decks_list'), callback_data='back_to_decks'))
    keyboard.add(InlineKeyboardButton(text=_('back_to_deck'), callback_data=f'deck_details_{slug}'))
    return keyboard.adjust(1, 2).as_markup()


# async def back_to_cardmanage(slug):
#     keyboard = InlineKeyboardBuilder()
#     keyboard.add(InlineKeyboardButton(text='Back to deck manage', callback_data='to_decks_list'))
