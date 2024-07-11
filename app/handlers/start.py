from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import app.keyboards as kb

router = Router()


@router.message(CommandStart())
@router.callback_query(F.data == 'to_main')
async def cmd_start(message: Message, state: FSMContext = None):
    if isinstance(message, Message):
        await message.answer('Добро пожаловать', reply_markup=kb.studying_start)
    elif state:
        await state.clear()
        await message.message.answer('Добро пожаловать', reply_markup=kb.studying_start)
