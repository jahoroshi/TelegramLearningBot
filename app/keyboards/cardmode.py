from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests import get_categories, get_category_item

# main = ReplyKeyboardMarkup(keyboard=[
#     [KeyboardButton(text='Каталог')],
#     [KeyboardButton(text='Корзина'), KeyboardButton(text='Контакты')]
# ],
#     resize_keyboard=True,
#     input_field_placeholder='Выбрать пункт меню.')

# main = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text='Каталог', callback_data='catalog')],
#     [InlineKeyboardButton(text='Корзина', callback_data='basket')],
#     [InlineKeyboardButton(text='Контакты', callback_data='contacts')]
# ],
#     resize_keyboard=True,
# input_field_placeholder='Выберите пункт!!!')

studying_start = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Start studying')], [KeyboardButton(text='Test asyncio')],
              [KeyboardButton(text='Decks')]],
    input_field_placeholder='Press to Start Studying', resize_keyboard=True)

mem_ratings22 = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Again'), KeyboardButton(text='Good'),
     KeyboardButton(text='Hard'), KeyboardButton(text='Easy')]
],
    resize_keyboard=True,
    input_field_placeholder='Select the recall level')


async def mem_ratings(ratings_count=None):
    rating_names = {1: 'Again', 2: 'Good', 3: 'Hard', 4: 'Easy'}
    keyboard = []
    for key, value in rating_names.items():
        if ratings_count:
            count = ratings_count[str(key)]
            keyboard.append(KeyboardButton(text=f'{value} ({count})'))
        else:
            keyboard.append(KeyboardButton(text=f'{value}'))
    a = ReplyKeyboardMarkup(keyboard=[keyboard], resize_keyboard=True,
                            input_field_placeholder='Select the recall level')
    return a


async def card_mode_buttons(buttons, update_names=None, order_scheme=None):
    keyboard = InlineKeyboardBuilder()
    button_names = {
        'show_back': 'Show back',
        'show_hint': 'Ask for hint',
        'show_similar': 'Show similar words',
        'show_first_letters': 'Show first letters',
        'scramble_letters': 'Scramble letters',
        'speech': '🔊'
    }
    if update_names:
        button_names.update(update_names)
    if order_scheme:
        buttons = {name: buttons.get(name, False) for name in order_scheme}
    for name, status in buttons.items():
        if status:
            keyboard.add(InlineKeyboardButton(text=button_names.get(name, name), callback_data=f'button_{name}'))
    keyboard.add(InlineKeyboardButton(text='Finish Training', callback_data='to_decks_list'))
    return keyboard.adjust(1, 2, 2, 2, repeat=True).as_markup()


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


async def quiz():
    ...


# async def scramble_letters_output(elements_count):
#     keyboard = InlineKeyboardBuilder()
#     similar_cyrillic = 'АОоСсI'
#     similar_latin = 'AoOCcl'
#     flag = None
#     for el, count in elements_count.items():
#         count = f' ({count})' if count > 1 else ''
#         mark = ''
#         if flag is None:
#             flag = True if el in similar_cyrillic else False if el in similar_latin else None
#         elif el in (similar_cyrillic, similar_latin)[flag]:
#             mark = "."
#         keyboard.add(
#             InlineKeyboardButton(text=f'{mark}{el if el != " " else "_"}{count}', callback_data=f'scramble_{el}'))
#     max_word = max(map(len, elements_count))
#     columns = (5, 3, 2)[(max_word > 0) + (max_word > 6) + (max_word > 15) - 1]
#     return keyboard.adjust(columns).as_markup()


async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'category_{category.id}'))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()


async def items(category_id):
    all_items = await get_category_item(category_id)
    keyboard = InlineKeyboardBuilder()
    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f'item_{item.id}'))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(1).as_markup()

# settings = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text='Button', url='https://google.com')]
# ])
#
# cars = ['Tesla', 'Mercedes', 'BMW', 'Van']
#
# async def inline_cars():
#     keyboard = InlineKeyboardBuilder()
#     for car in cars:
#         keyboard.add(InlineKeyboardButton(text=car, url='https://google.com'))
#     return keyboard.adjust(2).as_markup()
