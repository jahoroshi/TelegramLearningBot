from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.requests import send_request
from app.states import DeckViewingState, DeckRename
from app.middlewares.i18n_init import i18n
from settings import BASE_URL

_ = i18n.gettext


async def process_rename_deck(callback: CallbackQuery, state: FSMContext):
    """
    Processes the request to rename a deck by prompting the user for a new name.

    Args:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The finite state machine context for the user.
    """
    await callback.answer()
    slug = callback.data.split('_')[-1]
    await state.set_state(DeckRename.new_name)
    await state.update_data(slug=slug)

    # Prompt the user to enter a new name for the deck
    await callback.message.answer(
        _('enter_new_deck_name'),
        parse_mode=ParseMode.HTML
    )


async def process_rename_deck_handler(message: Message, state: FSMContext):
    """
    Processes the deck renaming after receiving the new name from the user.

    Args:
        message (Message): The message object containing the new deck name.
        state (FSMContext): The finite state machine context for the user.
    """
    data = await state.get_data()
    new_name = message.text

    # Validate the new deck name
    if len(new_name) > 100:
        text = _('max_100_chars')
        await message.answer(text)
        return

    if new_name and any(char.isalnum() for char in new_name):
        new_name = new_name.capitalize().strip()
        slug = data.get('slug')
        url = f'{BASE_URL}/api/v1/deck/manage/{slug}/'

        # Send a request to rename the deck
        response = await send_request(url, method='PUT', data={'name': new_name})
        status = response.get('status', 0)

        # Determine the response text based on the status code
        if status // 100 == 2:
            text = _('deck_name_changed')
            slug = response.get('data', {}).get('slug', slug)
        else:
            text = _('something_went_wrong')

        # Update the FSM state and display the response message
        await state.set_state(DeckViewingState.active)
        await message.answer(text, reply_markup=await kb.back_to_decklist_or_deckdetails(slug))
    else:
        text = _('name_letters_numbers')
        await message.answer(text)
