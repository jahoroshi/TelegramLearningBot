import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

import app.keyboards as kb
from app.services.deckhub.decklist import handle_decks_list_request
from app.requests import send_request
from app.states import DeckViewingState, DeckDelete
from app.utils import delete_two_messages
from app.middlewares.i18n_init import i18n
from settings import BASE_URL

_ = i18n.gettext


async def process_delete_deck_confirm(callback: CallbackQuery, state: FSMContext):
    """
    Processes the confirmation request to delete a deck.

    Args:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The finite state machine context for the user.
    """
    await callback.answer()
    await state.set_state(DeckDelete.active)
    slug = callback.data.split('_')[-1]
    text = _('confirm_delete_deck')

    # Update the message to ask for confirmation to delete the deck
    await callback.message.delete_reply_markup()
    await callback.message.answer(text, reply_markup=await kb.confirm_delete_desk(slug))


async def process_deck_delete(callback: CallbackQuery, state: FSMContext):
    """
    Processes the deck deletion request upon user confirmation.

    Args:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The finite state machine context for the user.
    """
    current_state = await state.get_state()
    await callback.answer()

    # Check if the current state allows for deck deletion
    if current_state == DeckDelete.active:
        slug = callback.data.split('_')[-1]
        url = f'{BASE_URL}/deck/api/v1/manage/{slug}/'

        # Send a DELETE request to remove the deck
        response = await send_request(url, method='DELETE')

        # Determine the response text based on the status code
        if response.get('status') == 204:
            text = _('deck_deleted')
            await callback.message.delete()

        else:
            text = _('something_went_wrong')
            await callback.message.delete_reply_markup()

        # Update the FSM state and display the response message
        await state.set_state(DeckViewingState.active)
        await callback.message.answer(text, reply_markup=kb.refresh_button)
        await asyncio.sleep(1.5)

    # Refresh the deck list
    await handle_decks_list_request(callback.message, state)
