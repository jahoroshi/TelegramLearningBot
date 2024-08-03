from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

import app.keyboards as kb
from app.utils.cardmode import gen_output_text
from app.middlewares.i18n_init import i18n

_ = i18n.gettext


async def process_show_first_letters(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    """
    Processes the logic to reveal the first letters of the card's back side.

    Args:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The finite state machine context for the user.
        data_store (dict, optional): The data store containing card information. Defaults to None.
    """
    card_data = data_store.get('card_data', {})
    front_side = card_data.get('front_side')
    prepared_text = card_data.get('back_side', '').split()
    max_len = max(map(len, prepared_text))

    step = callback.data.split('_')[-1]
    iteration = int(step) if step.isdigit() else 1

    # If iteration exceeds or equals the maximum length of any word, show the full text
    if step and iteration * 2 >= max_len:
        text = gen_output_text(card_data=card_data)
        await callback.message.edit_text(text, parse_mode=ParseMode.HTML)
        return

    # Mask the text, revealing only the specified number of letters
    masked_text = [
        word[:iteration * 2] + '*' * (len(word) - iteration * 2) if len(word) > iteration * 2 else word
        for word in prepared_text
    ]

    text = gen_output_text(front=front_side, extra_text='  '.join(masked_text))
    button_name = f'show_first_letters_{iteration + 1}'
    buttons = {button_name: True}
    letters_to_show = (iteration + 1) * 2

    # Adjust for odd-length words
    if max_len - iteration * 2 == 1:
        letters_to_show -= 1

    update_names = {
        button_name: _('show_letters_button').format(letters_to_show)
    }

    await callback.message.edit_text(
        text,
        reply_markup=await kb.card_mode_buttons(buttons, update_names=update_names),
        parse_mode=ParseMode.HTML
    )
