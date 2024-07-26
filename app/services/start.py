from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.requests import send_request
from settings import BASE_URL


async def set_initial_user_language(telegram_id, language) -> None:
    url = f'{BASE_URL}/users/api/v1/manage/{telegram_id}/'
    response = await send_request(url, method='PUT', data={'language': language})
    from app.middlewares import I18n
    I18n.current_locale = language
    return response
