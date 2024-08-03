from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.requests import send_request
from app.utils import create_deck_info
from app.middlewares.i18n_init import i18n
from settings import BASE_URL

_ = i18n.gettext


async def process_deck_details(callback_or_message: CallbackQuery or Message, state: FSMContext, slug=None):
    """
    Processes the request to display details of a specific deck.

    Args:
        callback_or_message (CallbackQuery or Message): The callback query or message object from the user.
        state (FSMContext): The finite state machine context for the user.
        slug (str, optional): The slug identifier for the deck. Defaults to None.
    """
    # Determine if the input is a callback query
    if isinstance(callback_or_message, CallbackQuery):
        message = callback_or_message.message
        slug = callback_or_message.data.split('_')[-1]
    else:
        message = callback_or_message

    # Build the request URL and fetch deck details
    url = f'{BASE_URL}/deck/api/v1/manage/{slug}/'
    response = await send_request(url)

    # If the request is successful, process and display the deck details
    if response.get('status') == 200:
        data = response.get('data')
        text = await create_deck_info(data)

        # Edit the message to show the deck details with management options
        await message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=await kb.manage_deck(data)
        )
    else:
        # Handle errors, e.g., when deck details are not available
        await message.answer(_('deck_details_error'))
