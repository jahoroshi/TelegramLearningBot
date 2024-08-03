from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.requests import send_request
from app.states import DeckCreate
from app.utils import display_message_and_redirect
from app.middlewares.i18n_init import i18n
from settings import BASE_URL

_ = i18n.gettext


async def process_deck_create(callback_or_message: CallbackQuery or Message, state: FSMContext):
    """
    Initiates the deck creation process by prompting the user for a deck name.

    Args:
        callback_or_message (CallbackQuery or Message): The callback query or message object from the user.
        state (FSMContext): The finite state machine context for the user.
    """
    # Determine if the input is a callback query and respond accordingly
    if isinstance(callback_or_message, CallbackQuery):
        await callback_or_message.answer()
        message = callback_or_message.message
    else:
        message = callback_or_message

    text = _('enter_deck_name')
    await message.answer(text, reply_markup=await kb.back())
    await state.set_state(DeckCreate.name)


async def process_deck_create_handler(message: Message, state: FSMContext):
    """
    Handles the deck creation process after receiving the deck name from the user.

    Args:
        message (Message): The message object containing the deck name.
        state (FSMContext): The finite state machine context for the user.
    """
    name = message.text
    telegram_id = state.key.user_id

    # Prepare the request data for deck creation
    data = {
        'name': name,
        'telegram_id': telegram_id,
    }
    url = f'{BASE_URL}/deck/api/v1/manage/'

    # Send a request to create the deck
    response = await send_request(url, method='POST', data=data)

    # Determine the response text based on the status code
    if response.get('status') == 201:
        text = _('deck_created_successfully')
    else:
        text = _('something_went_wrong')

    # Display the response message and redirect the user
    await display_message_and_redirect(message, state, text)
