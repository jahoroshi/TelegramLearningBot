from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

import app.keyboards as kb
# from app.middlewares import TestMiddleware
from app.services.cardmode import gen_output_text
from app.services.decorators import check_card_data

router = Router()

@router.callback_query(F.data.startswith('button_show_first_letters'))
@check_card_data
async def show_first_letters(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    card_data = data_store.get('card_data')
    front_side = card_data.get('front_side')
    prepared_text = card_data.get('back_side', '').split()
    max_len = max(map(len, prepared_text))

    step = callback.data.split('_')[-1]
    iteration = int(step) if step.isdigit() else 1

    if step and iteration * 2 >= max_len:
        text = gen_output_text(card_data=data_store.get('card_data', {}))
        await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN_V2)
        return

    masked_text = list(
        map(lambda x: x[:iteration * 2] + '*' * (len(x) - iteration * 2) if len(x) > iteration * 2 else x,
            prepared_text))

    text = gen_output_text(front=front_side, extra_text='  '.join(masked_text))
    button_name = f'show_first_letters_{iteration + 1}'
    buttons = {button_name: True}
    letters_to_show = (iteration + 1) * 2
    if max_len - iteration * 2 == 1:
        letters_to_show -= 1

    update_names = {
        button_name: f'Show {letters_to_show} letters'
    }

    await callback.message.edit_text(
        text,
        reply_markup=await kb.card_mode_buttons(buttons, update_names=update_names),
        parse_mode=ParseMode.MARKDOWN_V2)