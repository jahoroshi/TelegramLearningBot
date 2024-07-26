from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

import app.keyboards as kb
# from app.middlewares import TestMiddleware
from app.services.cardmode import gen_output_text
from app.services.decorators import check_card_data


router = Router()

@router.callback_query(F.data == 'button_scramble_letters')
@check_card_data
async def scramble_letters(callback: CallbackQuery, state: FSMContext, data_store: dict = None,
                           scrambled_segment: str = None, guessed_segment: str = None, is_sentence: bool = None):
    await callback.answer()
    if is_sentence is None:
        back_side = data_store.get('card_data', {}).get('back_side')
        is_sentence = len(elements := back_side.split()) > 3
        scrambled_segment = ' '.join(elements) if not is_sentence else elements
    elements_count = {el: scrambled_segment.count(el) for el in scrambled_segment}

    data = {
        'guessed_segment': guessed_segment or '',
        'scrambled_segment': scrambled_segment or '',
        'is_sentence': is_sentence,
    }
    await state.update_data(scrambler=data)

    front_side = data_store.get('card_data', {}).get("front_side")
    if guessed_segment:
        text = gen_output_text(front=front_side, extra_text=guessed_segment)
    else:
        text = gen_output_text(front=front_side)
    await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN_V2,
                                     reply_markup=await kb.scramble_letters_output(
                                         dict(sorted(elements_count.items()))))

@router.callback_query(F.data.startswith('scramble_'))
@check_card_data
async def scramble_letters_check(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    user_answer = callback.data.split('_')[1]
    scrambler = data_store.get('scrambler', {})
    scrambled_segment = scrambler.get('scrambled_segment')
    guessed_segment = scrambler.get('guessed_segment', '')
    is_sentence = scrambler.get('is_sentence')

    current_element = scrambled_segment[0]
    if current_element == user_answer:
        guessed_segment += current_element if not is_sentence else f'{current_element} '
        scrambled_segment = scrambled_segment[1:]
        if len(scrambled_segment) != 0:
            await scramble_letters(callback, state=state, scrambled_segment=scrambled_segment,
                                   guessed_segment=guessed_segment, is_sentence=is_sentence)
        else:
            card_data = data_store.get('card_data')
            text = gen_output_text(card_data=card_data)
            await callback.message.delete()
            await state.update_data(scrambler={})
            await callback.message.answer(text, parse_mode=ParseMode.MARKDOWN_V2)

    else:
        await callback.answer('🤯🥳 Incorrect. Please try again.')
        await scramble_letters(callback, state=state, scrambled_segment=scrambled_segment,
                               guessed_segment=guessed_segment, is_sentence=is_sentence)