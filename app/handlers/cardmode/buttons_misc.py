from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb

from app.handlers.cardmode.btns_set_rating import set_rating
from app.services.cardmode import gen_output_text
from app.services.decorators import check_card_data


router = Router()


async def send_message_card_mode(message: Message, buttons_to_show: dict, text: str):
    await message.answer(
        text=f'{text}',
        reply_markup=await kb.card_mode_buttons(buttons_to_show)
    )


@router.callback_query(F.data == 'card_is_already_known')
async def card_is_already_known(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await set_rating(callback.message, state=state, rating=5)


@router.callback_query(F.data == 'button_show_back')
@check_card_data
async def show_back(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    card_data = data_store.get('card_data')
    text = gen_output_text(card_data=card_data)
    await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN_V2)