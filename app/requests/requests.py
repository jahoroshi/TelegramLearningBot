import logging

import aiohttp


async def response_handler(response):
    if response.status // 100 == 2:
        content_type = response.headers.get('Content-Type')
        if content_type and content_type.startswith('audio'):
            data = await response.read()
        elif content_type and content_type.startswith('application/json'):
            data = await response.json()
        else:
            data = await response.text()
        return {'status': response.status, 'data': data}
    else:
        logging.error(f'!Error: {response.status}')
        return {'status': response.status}


async def send_request(url, method='GET', data=None):
    headers = {
        'X-API-Key': 'your-unique-api-key-here',
        'Content-Type': 'application/json'
    }
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
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
                    return await response_handler(response)

    except aiohttp.ClientError as e:
        text = f'Error in {__name__}\nClient Error: {e}\nUrl: {url}'
        logging.error(text)
        return {'error_detail': text}
    except Exception as e:
        text = f'Error in {__name__}\nClient Error: {e}\nUrl: {url}'
        logging.error(text)
        return {'error_detail': text}

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
