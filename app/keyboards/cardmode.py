from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests import get_categories, get_category_item
from app.middlewares.i18n_init import i18n

_ = i18n.gettext

async def mem_ratings(ratings_count=None):
    rating_names = {1: _('again'), 2: _('hard'), 3: _('good'), 4: _('easy')}
    keyboard = []
    for key, value in rating_names.items():
        if ratings_count:
            count = ratings_count[str(key)]
            keyboard.append(KeyboardButton(text=f'{value} ({count})'))
        else:
            keyboard.append(KeyboardButton(text=f'{value}'))
    a = ReplyKeyboardMarkup(
        keyboard=[keyboard],
        resize_keyboard=True,
        input_field_placeholder=_('select_recall_level')
    )
    return a


async def card_mode_buttons(buttons, update_names=None, order_scheme=None, is_first_show=None):
    keyboard = InlineKeyboardBuilder()
    rows = (1, 2, 2, 2)
    button_names = {
        'show_back': _('show_back'),
        'show_hint': _('ask_for_hint'),
        'show_similar': _('show_similar_words'),
        'show_first_letters': _('show_first_letters'),
        'scramble_letters': _('scramble_letters'),
        'speech': '🔊',
    }
    if update_names:
        button_names.update(update_names)
    if order_scheme:
        buttons = {name: buttons.get(name, False) for name in order_scheme}
    for name, status in buttons.items():
        if status:
            keyboard.add(InlineKeyboardButton(text=button_names.get(name, name), callback_data=f'button_{name}'))
    keyboard.add(InlineKeyboardButton(text=_('finish_training'), callback_data='to_decks_list'))
    if is_first_show:
        keyboard.add(InlineKeyboardButton(text=_('already_known'), callback_data='card_is_already_known'))
        rows = (1, 2, 2, 2, 1)

    # if buttons.get('speech') is False:
    #     rows = (1, 2, 2, 1, 1)
    return keyboard.adjust(*rows, repeat=True).as_markup()


async def similar_words_output(words):
    keyboard = InlineKeyboardBuilder()
    similar_words = set()
    back_side = words.get('back_side')
    for val in words.values():
        if isinstance(val, list):
            similar_words.update(val)
    for word in similar_words:
        status = 'correct' if word == back_side else 'incorrect'
        keyboard.add(InlineKeyboardButton(text=word, callback_data=f'similar_{status}'))
    max_word = max(map(len, similar_words))
    columns = (3, 2, 1)[(max_word > 1) + (max_word > 15) + (max_word > 20) - 1]
    return keyboard.adjust(columns).as_markup()


async def scramble_letters_output(elements_count):
    keyboard = InlineKeyboardBuilder()
    similar_lat = {'A': 'А', 'O': 'О', 'o': 'о', 'C': 'С', 'c': 'с', 'I': 'l', 'K': 'К', 'P': 'Р', 'p': 'р', 'E': 'Е',
                   'B': 'В', 'H': 'Н', 'X': 'Х', 'T': 'Т'}
    similar_cyr = {'А': 'A', 'О': 'O', 'о': 'o', 'С': 'C', 'с': 'c', 'l': 'I', 'К': 'K', 'Р': 'P', 'р': 'p', 'Е': 'E',
                   'В': 'B', 'Н': 'H', 'Х': 'X', 'Т': 'T'}
    encountered_letters = set()
    letter_mapping = {}
    for el, count in elements_count.items():
        count = f' ({count})' if count > 1 else ''
        mark = ''
        if not letter_mapping:
            letter_mapping = similar_cyr if el in similar_cyr else similar_lat if el in similar_lat else {}

        if letter_mapping:
            if el in letter_mapping:
                encountered_letters.add(letter_mapping[el])
            elif el in encountered_letters:
                mark = '.'

        keyboard.add(
            InlineKeyboardButton(text=f'{mark}{el if el != " " else "_"}{count}', callback_data=f'scramble_{el}'))
    max_word = max(map(len, elements_count))
    columns = (5, 3, 2)[(max_word > 0) + (max_word > 6) + (max_word > 15) - 1]
    return keyboard.adjust(columns).as_markup()
