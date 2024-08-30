from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.middlewares.locales import i18n, i18n_middleware
_ = i18n.gettext



async def account_settings():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('change_language'), callback_data='change_language'))
    return keyboard.adjust(1).as_markup()


async def change_language():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='English', callback_data='new_language_en'))
    keyboard.add(InlineKeyboardButton(text='Русский', callback_data='new_language_ru'))
    keyboard.add(InlineKeyboardButton(text=_('back_to_decks_list'), callback_data='back_to_decks'))

    return keyboard.adjust(2, 1).as_markup()


