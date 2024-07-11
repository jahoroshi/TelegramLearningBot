import logging

import aiohttp

async def response_handler(response):
    if response.status // 100 == 2:
        if response.headers.get('Content-Type').startswith('audio'):
            data = await response.read()
        else:
            data = await response.json()
        return data
    else:
        logging.error(f'!Error: {response.status}')
        return None


async def send_request(url, method='GET', data=None):
    try:
        async with aiohttp.ClientSession() as session:
            if method == 'GET':
                async with session.get(url) as response:
                    return await response_handler(response)
            elif method == 'POST':
                async with session.post(url, json=data) as response:
                    return await response_handler(response)
            elif method == 'PUT':
                async with session.put(url, json=data) as response:
                    return await response_handler(response)
            elif method == 'DELETE':
                async with session.delete(url, json=data) as response:
                    return response.status

    except aiohttp.ClientError as e:
        print(
            f'Client Error: {e}',
            f'Url: {url}'
        )
        return None
    except Exception as e:
        print(
            f'Error in {__name__}: {e}',
            f'Url: {url}'
        )
        return None



# async def set_data(url, data):
#     try:
#         async with aiohttp.ClientSession() as session:
#             async with session.post(url, json=data) as response:
#                 if response.status == 200:
#                     response_data = await response.json()
#                     return response_data
#                 else:
#                     print(f'Error: {response.status}')
#                     return None
#     except aiohttp.ClientError as e:
#         print(f'Client Error: {e}')
#         return None
#     except Exception as e:
#         print(f'Error: {e}')
#         return None
