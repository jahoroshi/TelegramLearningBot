from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.handlers.cardmode.cardmode_start import card_mode
# from app.middlewares import TestMiddleware
from app.requests import send_request
from app.services.decorators import check_card_data


from settings import BASE_URL

router = Router()


@router.message(F.text.in_({'Again', 'Good', 'Hard', 'Easy'}))
@check_card_data
async def set_rating(message: Message, state: FSMContext, data_store: dict = None, rating=None):
    if rating is None:
        ratings = {'Again': 1,
                   'Hard': 2,
                   'Good': 3,
                   'Easy': 4,
                   }
        text = message.text
        rating = ratings[text]
    if rating == 4:
        data = await state.get_data()
        data['completed_cards'] = data.get('completed_cards', 0) + 1
        await state.update_data(data)

    mappings_id = data_store.get('card_data', {}).get('mappings_id')
    url_get_card = data_store.get('start_config', {}).get('urls', {}).get('get_card')
    requests_data = {
        'mappings_id': mappings_id,
        'rating': rating,
    }
    response = await send_request(f"{BASE_URL}{url_get_card}", method='POST', data=requests_data)
    new_card_data = response.get('data')
    await card_mode(message, state, card_data=new_card_data)