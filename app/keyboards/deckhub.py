import os
from datetime import datetime

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.middlewares.i18n_init import i18n
from settings import BASE_URL

from dotenv import load_dotenv

load_dotenv()
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
        keyboard.add(InlineKeyboardButton(text=f'✿ {name}', callback_data=f'{callback_prefix}_{deck["slug"]}'))
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
    rows = [2, 2]

    if new_cards_count:
        keyboard.add(InlineKeyboardButton(text=_('study_new'), callback_data=f'choose_study_client_{slug}_new'))
        rows.insert(0, 1)
    if reviews_count:
        keyboard.add(InlineKeyboardButton(text=_('review_cards'), callback_data=f'choose_study_client_{slug}_review'))
        rows.insert(0, 1)
    keyboard.add(InlineKeyboardButton(text=_('show_cards'), callback_data=f'show_cards_{slug}'))
    keyboard.add(InlineKeyboardButton(text=_('import_cards'), callback_data=f'import_cards_{slug}'))
    keyboard.add(InlineKeyboardButton(text=_('deck_manage'), callback_data=f'manage_deck_edit_del_{slug}'))
    keyboard.add(InlineKeyboardButton(text=_('back_to_decks'), callback_data=f'back_to_decks'))
    return keyboard.adjust(*rows).as_markup()


async def manage_deck_edit_del_res(slug):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('rename_deck'), callback_data=f'rename_deck_{slug}'))
    keyboard.add(InlineKeyboardButton(text=_('delete_deck'), callback_data=f'delete_deck_{slug}'))
    keyboard.add(InlineKeyboardButton(text=_('reset_progress'), callback_data=f'reset_progress_{slug}'))
    keyboard.add(InlineKeyboardButton(text=_('back_to_decks_list'), callback_data='back_to_decks'))
    keyboard.add(InlineKeyboardButton(text=_('back_to_deck'), callback_data=f'deck_details_{slug}'))
    return keyboard.adjust(1, 1, 1, 2).as_markup()


async def reset_deck_progress(slug):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('reset'), callback_data=f'reset_deck_confirm_{slug}'))
    keyboard.add(InlineKeyboardButton(text=_('back_to_deck_manage'), callback_data=f'manage_deck_edit_del_{slug}'))
    return keyboard.adjust(2).as_markup()


async def back():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('back_to_decks'), callback_data='back_to_decks'))
    return keyboard.as_markup()


async def confirm_delete_desk(slug):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('delete'), callback_data=f'confirm_delete_deck_{slug}'))
    keyboard.add(InlineKeyboardButton(text=_('back'), callback_data='to_decks_list'))
    return keyboard.as_markup()


async def deckhub_manage_button():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('manage'), callback_data=f'deckhub_manage'))


async def deckhub_manage_actions():
    keyword = InlineKeyboardBuilder()
    keyword.add(InlineKeyboardButton(text=_('create_new_deck'), callback_data=f'deck_create'))
    keyword.add(InlineKeyboardButton(text=_('delete_deck'), callback_data=f'deck_delete'))


async def back_to_decklist_or_deckdetails_btns(slug):
    btn1 = InlineKeyboardButton(text=_('back_to_decks_list'), callback_data='back_to_decks')
    btn2 = InlineKeyboardButton(text=_('back_to_deck'), callback_data=f'deck_details_{slug}')
    return btn1, btn2


async def back_to_decklist_or_deckdetails(slug):
    btn1, btn2 = await back_to_decklist_or_deckdetails_btns(slug)
    keyboard = InlineKeyboardBuilder()
    keyboard.add(btn1)
    keyboard.add(btn2)
    return keyboard.as_markup()

async def back_to_decklist_or_details_addcard(slug):
    btn1, btn2 = await back_to_decklist_or_deckdetails_btns(slug)
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('add_card'), callback_data=f'add_card_{slug}'))
    keyboard.add(btn1)
    keyboard.add(btn2)
    return keyboard.adjust(1, 2).as_markup()

async def create_new_deck():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('create_new_deck'), callback_data=f'deck_create'))
    return keyboard.as_markup()

async def choose_study_format(slug, study_mode, study_client):
    keyboard = InlineKeyboardBuilder()
    rows = (2,)
    text_mode_params = {'text': _('study_format_text')}
    audio_mode_params = {'text': _('study_format_audio')}
    if 'web_app' in study_client:
        telegram_id = study_client['web_app']
        url = '{}/api/v1/study/web_app/{}?mode={}&slug={}&format={}' + f'&api-key={os.getenv("SERVER-TOKEN")}'
        text_mode_params.update({'web_app': WebAppInfo(url=url.format(BASE_URL, telegram_id, study_mode, slug, 'text'))})
        audio_mode_params.update({'web_app': WebAppInfo(url=url.format(BASE_URL, telegram_id, study_mode, slug, 'audio'))})
        btn1, btn2 = await back_to_decklist_or_deckdetails_btns(slug)
    else:
        text_mode_params.update({'callback_data': f'start_studying_{slug}_{study_mode}_text'})
        audio_mode_params.update({'callback_data': f'start_studying_{slug}_{study_mode}_audio'})

    keyboard.add(
        InlineKeyboardButton(**text_mode_params))
    if 'callback_data' in audio_mode_params:
        keyboard.add(
            InlineKeyboardButton(**audio_mode_params))

    if 'btn2' in locals():
        keyboard.add(btn2)
        rows = (1, 1)
    return keyboard.adjust(*rows).as_markup()


async def choose_study_client(slug, study_mode):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text=_('study_client_web_app'), callback_data=f'choose_format_{slug}_{study_mode}_webapp'))
    keyboard.add(
        InlineKeyboardButton(text=_('study_client_chat'), callback_data=f'choose_format_{slug}_{study_mode}_chat'))
    return keyboard.adjust(2).as_markup()


refresh_button = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=_('refresh'))]],
    input_field_placeholder=_('press_to_start_studying'), resize_keyboard=True)

create_new_deck_button = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=_('create_deck'))]],
    input_field_placeholder=_('press_to_start_studying'), resize_keyboard=True)


async def generate_available_button(review_date):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=_('next_review').format(int(review_date)))]],
        input_field_placeholder=_('card_will_be_available'), resize_keyboard=True)


async def main_button(decks_data):
    main_button_review = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=_('review_all_decks'))]],
        input_field_placeholder=_('press_to_start_studying'), resize_keyboard=True)

    main_button_addcard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=_('add_card'))]],
        input_field_placeholder=_('press_to_start_studying'), resize_keyboard=True)

    main_button_new = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=_('study_all_decks'))]],
        input_field_placeholder=_('press_to_start_studying'), resize_keyboard=True)

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
