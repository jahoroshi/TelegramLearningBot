from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

import app.keyboards as kb
from app.middlewares.i18n_init import i18n

_ = i18n.gettext

router = Router()


@router.message(Command(commands=['help']))
async def get_help(message: Message):
    text = _(
        "help_description"
    )
    await message.answer(text, reply_markup=await kb.back(), parse_mode=ParseMode.HTML)
