from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

import app.keyboards as kb
from app.utils.cardmode import gen_output_text
from app.middlewares.i18n_init import i18n

_ = i18n.gettext


async def process_scramble_letters(callback: CallbackQuery, state: FSMContext, data_store: dict = None,
                                   scrambled_segment: str = None, guessed_segment: str = None,
                                   is_sentence: bool = None):
    """
    Processes the logic to initiate the scrambling of letters from the card's back side.

    Args:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The finite state machine context for the user.
        data_store (dict, optional): The data store containing card information. Defaults to None.
        scrambled_segment (str, optional): The segment of the card text that is scrambled. Defaults to None.
        guessed_segment (str, optional): The segment of the card text that has been guessed. Defaults to None.
        is_sentence (bool, optional): Whether the card's back side is treated as a sentence. Defaults to None.
    """
    await callback.answer()

    # Initialize or reset scrambled segments and guessed segments
    if is_sentence is None:
        back_side = data_store.get('card_data', {}).get('back_side')
        is_sentence = len(elements := back_side.split()) > 3
        scrambled_segment = elements if is_sentence else ' '.join(elements)

    elements_count = {el: scrambled_segment.count(el) for el in scrambled_segment}

    data = {
        'guessed_segment': guessed_segment or '',
        'scrambled_segment': scrambled_segment or '',
        'is_sentence': is_sentence,
    }
    await state.update_data(scrambler=data)

    front_side = data_store.get('card_data', {}).get("front_side")

    # Generate output text for user
    if guessed_segment:
        text = gen_output_text(front=front_side, extra_text=guessed_segment)
    else:
        text = gen_output_text(front=front_side)

    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=await kb.scramble_letters_output(dict(sorted(elements_count.items())))
    )


async def process_scramble_letters_check(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    """
    Processes the logic to check the user's input against the scrambled letters.

    Args:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The finite state machine context for the user.
        data_store (dict, optional): The data store containing card information. Defaults to None.
    """
    user_answer = callback.data.split('_')[1]
    scrambler = data_store.get('scrambler', {})
    scrambled_segment = scrambler.get('scrambled_segment')
    guessed_segment = scrambler.get('guessed_segment', '')
    is_sentence = scrambler.get('is_sentence')

    # Validate the user's input
    current_element = scrambled_segment[0]
    if current_element == user_answer:
        guessed_segment += current_element if not is_sentence else f'{current_element} '
        scrambled_segment = scrambled_segment[1:]

        # If the entire segment is guessed, show the final output
        if len(scrambled_segment) != 0:
            await process_scramble_letters(
                callback,
                state=state,
                data_store=data_store,
                scrambled_segment=scrambled_segment,
                guessed_segment=guessed_segment,
                is_sentence=is_sentence
            )
        else:
            card_data = data_store.get('card_data')
            text = gen_output_text(card_data=card_data)
            await callback.message.delete()
            await state.update_data(scrambler={})
            await callback.message.answer(text, parse_mode=ParseMode.HTML)
    else:
        # If the answer is incorrect, prompt the user to try again
        await callback.answer(_('incorrect_try_again'))
        await process_scramble_letters(
            callback,
            state=state,
            data_store=data_store,
            scrambled_segment=scrambled_segment,
            guessed_segment=guessed_segment,
            is_sentence=is_sentence
        )
