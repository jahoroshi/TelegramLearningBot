from app.requests import send_request
from settings import BASE_URL


# async def get_language_or_create_user(telegram_id: int, telegram_username: str) -> str or None:
#     url = f'{BASE_URL}/users/api/v1/manage/{telegram_id}/?username={telegram_username}'
#     response = await send_request(url, method='GET')
#     status = response.get('status')
#     if status == 200:
#         return response.get('data', {}).get('language')
#     elif status == 201:
#         return None
#     else:
#         return 'en'
#
# async def get_language(telegram_id: int) -> str or None:
#     url = f'{BASE_URL}/users/api/v1/manage/{telegram_id}/'
#     response = await send_request(url, method='GET')
#     status = response.get('status')
#     if status == 200:
#         return response.get('data', {}).get('language', 'no language')
#     elif status == 404:
#         return 'no user'
#     else:
#         return None


async def get_or_create_user(telegram_id: int, telegram_username: str) -> str or None:
    url = f'{BASE_URL}/users/api/v1/manage/{telegram_id}/?username={telegram_username}'
    response = await send_request(url, method='GET')
    status = response.get('status')
    if isinstance(status, int) and status // 100 == 2:
        return response.get('data', {})
    else:
        return None
