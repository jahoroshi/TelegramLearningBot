from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.middlewares.i18n_init import i18n

_ = i18n.gettext


async def show_cards_action_buttons(slug, pagination=None, cur_page=None):
    keyboard = InlineKeyboardBuilder()
    rows = [3, 2]
    if pagination:
        for i in range(1, pagination+1):
            text = f'{i}'
            if i == cur_page:
                text = f'「{i}」'
            keyboard.add(InlineKeyboardButton(text=text, callback_data=f'show_card_pag_{i}'))
        rem = pagination % 8
        count = (pagination - rem) // 8
        pages = [[8 for i in range(count)] + [rem] if rem > 0 else [8 for i in range(count)]][0]
        rows = pages + rows

    keyboard.add(InlineKeyboardButton(text=_('add_card'), callback_data=f'add_card_{slug}'))
    keyboard.add(InlineKeyboardButton(text=_('edit_card'), callback_data=f'edit_card_{slug}'))
    keyboard.add(InlineKeyboardButton(text=_('delete_card'), callback_data=f'delete_card_{slug}'))
    keyboard.add(InlineKeyboardButton(text=_('back_to_decks_list'), callback_data='back_to_decks'))
    keyboard.add(InlineKeyboardButton(text=_('back_to_deck'), callback_data=f'deck_details_{slug}'))
    return keyboard.adjust(*rows).as_markup()


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
