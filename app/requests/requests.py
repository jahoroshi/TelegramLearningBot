import logging

import aiohttp


async def response_handler(response):
    if response.status // 100 == 2:
        if response.status == 204:
            return {'status': response.status, 'data': None}

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
        text = f'>> aiohttp.ClientError in {__name__}\n>> Client Error: {e}\n>> Url: {url}'
        logging.error(text)
        print(text)
        return {'status': 'error', 'error_detail': text}
    except Exception as e:
        text = f'>> General Error in {__name__}\n>> Client Error: {e}\n>> Url: {url}'
        logging.error(text)
        return {'status': 'error', 'error_detail': text}

