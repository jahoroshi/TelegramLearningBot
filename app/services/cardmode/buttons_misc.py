from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.services.cardmode.btns_set_rating import process_set_rating
from app.utils.cardmode import gen_output_text


async def process_card_already_known(callback: CallbackQuery, state: FSMContext):
    """
    Processes the logic for marking a card as already known.

    Args:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The finite state machine context for the user.
    """
    await callback.answer()
    await process_set_rating(callback.message, state=state, rating=5)


async def process_show_back(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    """
    Processes the logic for showing the back side of the card.

    Args:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The finite state machine context for the user.
        data_store (dict, optional): The data store containing card information. Defaults to None.
    """
    card_data = data_store.get('card_data')
    data = await state.get_data()
    study_format = data_store.get('start_config', {}).get('study_format')
    completed_cards = data.get('completed_cards', 0)
    card_data['ratings_count']['4'] = completed_cards

    # Prepare the message parameters
    params = {
        'text': gen_output_text(card_data=card_data),
        'parse_mode': ParseMode.HTML,
    }

    # Display the back side of the card based on the study format
    if study_format == 'text':
        await callback.message.edit_text(**params)
    else:
        await callback.message.delete_reply_markup()
        await callback.message.answer(**params)
