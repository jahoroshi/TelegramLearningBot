from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

async def choose_language(language):
    keyboard = InlineKeyboardBuilder()
    if 'ru' in language:
        keyboard.add(InlineKeyboardButton(text='Продолжить', callback_data='set_language_ru'))
    if 'en' in language:
        keyboard.add(InlineKeyboardButton(text='Continue', callback_data='set_language_en'))
    return keyboard.adjust(1).as_markup()
