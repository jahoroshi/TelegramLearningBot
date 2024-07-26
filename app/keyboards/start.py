from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def choose_language(language):
    keyboard = InlineKeyboardBuilder()
    if 'ru' in language:
        keyboard.add(InlineKeyboardButton(text='Продолжить', callback_data='set_language_ru'))
    if 'en' in language:
        keyboard.add(InlineKeyboardButton(text='Continue', callback_data='set_language_en'))
    return keyboard.adjust(1).as_markup()


studying_start = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Create deck')],
              [KeyboardButton(text='REFRESH')]],
    input_field_placeholder='Press to Start Studying', resize_keyboard=True)
