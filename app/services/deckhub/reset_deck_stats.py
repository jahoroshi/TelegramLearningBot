import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

import app.keyboards as kb
from app.services.deckhub.decklist import handle_decks_list_request
from app.requests import send_request
from app.states import DeckViewingState
from app.states import ResetDeckProgress
from app.middlewares.i18n_init import i18n
from settings import BASE_URL

_ = i18n.gettext


async def process_reset_deck_progress_confirm(callback: CallbackQuery, state: FSMContext):
    """
    Processes the confirmation request to reset a deck's progress.

    Args:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The finite state machine context for the user.
    """
    slug = callback.data.split('_')[-1]
    await state.set_state(ResetDeckProgress.active)

    # Update the message to confirm the reset of deck progress
    text = _('reset_progress_confirmation')
    await callback.message.edit_text(text, reply_markup=await kb.reset_deck_progress(slug))


async def process_reset_deck_progress_handler(callback: CallbackQuery, state: FSMContext):
    """
    Processes the request to reset a deck's progress upon user confirmation.

    Args:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The finite state machine context for the user.
    """
    current_state = await state.get_state()

    # Ensure the state allows for resetting deck progress
    if current_state == ResetDeckProgress.active:
        slug = callback.data.split('_')[-1]
        telegram_id = state.key.user_id
        url = f'{BASE_URL}/api/v1/deck/manage/reset/{telegram_id}/{slug}/'

        # Send a request to reset the deck progress
        response = await send_request(url, method='GET')

        # Determine the response text based on the status code
        if response.get('status') == 200:
            text = _('deck_reset_success')
        elif response.get('status') == 204:
            text = _('deck_is_empty')
        else:
            text = _('something_went_wrong')

        # Update the FSM state and display the response message
        await callback.message.delete_reply_markup()
        await state.set_state(DeckViewingState.active)
        await callback.message.answer(text, reply_markup=kb.refresh_button)
        await asyncio.sleep(2)

    # Refresh the deck list
    await handle_decks_list_request(callback.message, state)
