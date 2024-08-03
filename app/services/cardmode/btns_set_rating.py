from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.requests import send_request
from app.services.cardmode.cardmode_start import process_card_mode
from app.middlewares.i18n_init import i18n
from settings import BASE_URL

_ = i18n.gettext


async def process_set_rating(message: Message, state: FSMContext, data_store: dict = None, rating=None):
    """
    Processes the user's card rating and updates the card's status.

    Args:
        message (Message): The message object from the user.
        state (FSMContext): The finite state machine context for the user.
        data_store (dict, optional): The data store containing card information. Defaults to None.
        rating (int, optional): The rating given by the user. Defaults to None.
    """
    # Determine the rating if not provided
    if rating is None:
        ratings = {
            _("again"): 1,
            _("hard"): 2,
            _("good"): 3,
            _("easy"): 4,
        }
        text = message.text
        rating = ratings[text]

    # Increment completed cards count for the easiest rating
    if rating == 4:
        data = await state.get_data()
        data['completed_cards'] = data.get('completed_cards', 0) + 1
        await state.update_data(data)

    mappings_id = data_store.get('card_data', {}).get('mappings_id')
    url_get_card = data_store.get('start_config', {}).get('urls', {}).get('get_card')

    # Prepare the request data to send to the server
    requests_data = {
        'mappings_id': mappings_id,
        'rating': rating,
    }

    # Send the rating to the server and get the next card
    response = await send_request(f"{BASE_URL}{url_get_card}", method='POST', data=requests_data)
    new_card_data = response.get('data')

    # Start the card mode with the new card data
    await process_card_mode(message, state, card_data=new_card_data)
