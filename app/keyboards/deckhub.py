from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.middlewares.locales import i18n

from datetime import datetime

_ = i18n.gettext


async def deck_names(data, is_quick_add=None):
    keyboard = InlineKeyboardBuilder()
    if not is_quick_add:
        callback_prefix = 'deck_details'
    else:
        callback_prefix = 'addcard_slug'
    rows = ()
    for deck in data:
        name = deck['name']
        keyboard.add(InlineKeyboardButton(text=f'➲ {name}', callback_data=f'{callback_prefix}_{deck["slug"]}'))
    # keyboard.add(InlineKeyboardButton(text=_('create_deck_ddn'), callback_data='deck_create'))
    #
    # match len(data):
    #     case 1:
    #         rows = (1, 1)
    #     case 2:
    #         rows = (2, 1)
    #     case 3:
    #         rows = (3, 1)
    #     case n if n % 2 == 0:
    #         rows = (2, 2)
    #     case n if n % 3 == 0:
    #         rows = (3, 1)

    return keyboard.adjust(3).as_markup()


async def manage_deck(deck):
    keyboard = InlineKeyboardBuilder()
    new_cards_count = deck.get('new_cards_count')
    reviews_count = deck.get('reviews_count')
    slug = deck.get('slug')
    rows = [3, 2]

    if new_cards_count:
        keyboard.add(InlineKeyboardButton(text='Study new', callback_data=f'choose_study_format_{slug}_new'))
        rows.insert(0, 1)
    if reviews_count:
        keyboard.add(InlineKeyboardButton(text='Review cards', callback_data=f'choose_study_format_{slug}_review'))
        rows.insert(0, 1)
    keyboard.add(InlineKeyboardButton(text='Show cards', callback_data=f'show_cards_{slug}'))
    keyboard.add(InlineKeyboardButton(text='Import cards', callback_data=f'import_cards_{slug}'))
    keyboard.add(InlineKeyboardButton(text='Add card', callback_data=f'add_card_{slug}'))
    keyboard.add(InlineKeyboardButton(text='Deck manage', callback_data=f'manage_deck_edit_del_{slug}'))
    keyboard.add(InlineKeyboardButton(text='« Back to decks', callback_data=f'back_to_decks'))
    return keyboard.adjust(*rows).as_markup()


async def manage_deck_edit_del_res(slug):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='✎ Rename deck', callback_data=f'rename_deck_{slug}'))
    keyboard.add(InlineKeyboardButton(text='× Delete deck', callback_data=f'delete_deck_{slug}'))
    keyboard.add(InlineKeyboardButton(text='Reset Progress', callback_data=f'reset_progress_{slug}'))
    keyboard.add(InlineKeyboardButton(text='« Back to decks list', callback_data='back_to_decks'))
    keyboard.add(InlineKeyboardButton(text='« Back to deck', callback_data=f'deck_details_{slug}'))
    return keyboard.adjust(2, 1, 2).as_markup()


async def reset_deck_progress(slug):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Reset', callback_data=f'reset_deck_confirm_{slug}'))
    keyboard.add(InlineKeyboardButton(text='« Back to deck manage', callback_data=f'manage_deck_edit_del_{slug}'))
    return keyboard.adjust(2).as_markup()


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


async def back_to_decklist_or_deckdetails(slug):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='« Back to decks list', callback_data='back_to_decks'))
    keyboard.add(InlineKeyboardButton(text='« Back to deck', callback_data=f'deck_details_{slug}'))
    return keyboard.as_markup()



async def create_new_deck():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Create new deck', callback_data=f'deck_create'))
    return keyboard.as_markup()


async def choose_study_format(slug, study_mode):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text=_('study_format_text'), callback_data=f'start_studying_{slug}_{study_mode}_text'))
    keyboard.add(
        InlineKeyboardButton(text=_('study_format_audio'), callback_data=f'start_studying_{slug}_{study_mode}_audio'))
    return keyboard.adjust(2).as_markup()


refresh_button = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='REFRESH')]],
    input_field_placeholder='Press to Start Studying', resize_keyboard=True)

create_new_deck_button = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Create deck')]],
    input_field_placeholder='Press to Start Studying', resize_keyboard=True)

main_button_review = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Review all decks')]],
    input_field_placeholder='Press to Start Studying', resize_keyboard=True)

main_button_addcard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Add card')]],
    input_field_placeholder='Press to Start Studying', resize_keyboard=True)

main_button_new = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Study all decks')]],
    input_field_placeholder='Press to Start Studying', resize_keyboard=True)


async def generate_available_button(review_date):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=f"⏰ Next review will be in {int(review_date)}h.")]],
        input_field_placeholder='Card will be available:', resize_keyboard=True)


async def main_button(decks_data):
    if any(deck['reviews_count'] != 0 for deck in decks_data):
        return main_button_review
    cards_count = any(deck['cards_count'] for deck in decks_data)
    new_cards_count = any(deck['new_cards_count'] for deck in decks_data)
    min_review_date = min(
        (deck['min_review_date'] for deck in decks_data if deck['min_review_date']),
        default=None
    )

    if cards_count is False:
        return main_button_addcard
    else:
        if new_cards_count:
            return main_button_new
        elif min_review_date:
            cur_time_str = decks_data[0]['current_time']
            current_time = datetime.fromisoformat(cur_time_str.replace("Z", "+00:00"))
            next_review_datetime = datetime.fromisoformat(min_review_date.replace("Z", "+00:00"))
            time_until_next_review = next_review_datetime - current_time
            hours_until_next_review = time_until_next_review.total_seconds() / 3600
            return await generate_available_button(hours_until_next_review)
        else:
            return main_button_addcard
