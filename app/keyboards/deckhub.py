from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def deck_names(data):
    keyboard = InlineKeyboardBuilder()
    for deck in data:
        name = deck['name']
        keyboard.add(InlineKeyboardButton(text=name, callback_data=f'deck_details_{deck["slug"]}'))
    return keyboard.adjust(3).as_markup()


# async def get_training_modes(deck):
#     keyboard = InlineKeyboardBuilder()
#
#     new_cards_count = deck.get('new_cards_count')
#     reviews_count = deck.get('reviews_count')
#     slug = deck.get('slug')
#
#     if new_cards_count:
#         keyboard.add(InlineKeyboardButton(text='Study new', callback_data=f'start_studying_{slug}_new'))
#     if reviews_count:
#         keyboard.add(InlineKeyboardButton(text='Review cards', callback_data=f'start_studying_{slug}_review'))
#     return keyboard.adjust(3, 2).as_markup()


async def manage_deck(deck):
    keyboard = InlineKeyboardBuilder()
    new_cards_count = deck.get('new_cards_count')
    reviews_count = deck.get('reviews_count')
    slug = deck.get('slug')
    rows = [3, 2]

    if new_cards_count:
        keyboard.add(InlineKeyboardButton(text='Study new', callback_data=f'start_studying_{slug}_new'))
        rows = [1] + rows
    if reviews_count:
        keyboard.add(InlineKeyboardButton(text='Review cards', callback_data=f'start_studying_{slug}_review'))
        rows = [1] + rows
    keyboard.add(InlineKeyboardButton(text='Show cards', callback_data=f'show_cards_{slug}'))
    keyboard.add(InlineKeyboardButton(text='Import cards', callback_data=f'import_cards_{slug}'))
    keyboard.add(InlineKeyboardButton(text='Add card', callback_data=f'add_card_{slug}'))
    keyboard.add(InlineKeyboardButton(text='✎ Rename deck', callback_data=f'rename_deck_{slug}'))
    keyboard.add(InlineKeyboardButton(text='× Delete deck', callback_data=f'delete_deck_{slug}'))
    keyboard.add(InlineKeyboardButton(text='« Back to decks', callback_data=f'back_to_decks'))
    return keyboard.adjust(*rows).as_markup()


async def back():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='« Back to decks', callback_data='back_to_decks'))
    return keyboard.as_markup()


async def confirm_delete_desk(slug):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Delete', callback_data=f'confirm_delete_deck_{slug}'))
    keyboard.add(InlineKeyboardButton(text='Back', callback_data='to_decks_list'))
    return keyboard.as_markup()


async def deckhub_manage_button():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='manage', callback_data=f'deckhub_manage'))


async def deckhub_manage_actions():
    keyword = InlineKeyboardBuilder()
    keyword.add(InlineKeyboardButton(text='Add new deck', callback_data=f'deck_create'))
    keyword.add(InlineKeyboardButton(text='Delete deck', callback_data=f'deck_delete'))


refresh_session = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='REFRESH')]],
                                      input_field_placeholder='Press to button', resize_keyboard=True)


async def back_to_decklist_or_deckdetails(slug):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='« Back to decks list', callback_data='back_to_decks'))
    keyboard.add(InlineKeyboardButton(text='« Back to deck', callback_data=f'deck_details_{slug}'))
    return keyboard.as_markup()

# is_two_sides = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Yes'), KeyboardButton(text='No')]],
#                                    one_time_keyboard=True)
