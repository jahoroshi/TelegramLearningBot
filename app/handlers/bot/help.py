from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

import app.keyboards as kb

router = Router()


@router.message(Command(commands=['help']))
async def get_help(message: Message):
    text = '<b><i>Добавляйте Карточки Легко и Быстро!</i></b> 🌟 Привет! 😊 Мы упростили процесс добавления карточек. Теперь вы можете быстро добавить <b>слово</b> или <b>предложение</b> из любого приложения или браузера. Просто выделите нужный текст, нажмите «Поделиться» 📤 и выберите Телеграм, чтобы отправить нашему <b>АнкиБоту</b> 🤖 .\n\n✍ Вы можете заполнить поле «<b>Добавить комментарий</b>», чтобы создать вторую сторону карточки, или оставить его пустым и добавить вторую сторону позже в окне <b>чата</b>.\n\n🧩 Как только я получу оба сообщения, я пойму, что вы хотите добавить новую карточку, и предложу выбрать подходящую <b>категорию</b> 🗂️. Всё <b>быстро</b> и <b>просто</b>! Удачи! ✨'
    await message.answer(text, reply_markup=await kb.back(), parse_mode=ParseMode.HTML)
