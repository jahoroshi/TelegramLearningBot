import asyncio
import re
from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.requests import send_request
from bot import bot

import app.keyboards as kb
from settings import BASE_URL


async def data_handler(data):
    days = data.days
    hours, remainder = divmod(data.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if days:
        text = f'{days}d : {hours}h : {minutes} min'
    else:
        text = f'{hours}h : {minutes}min'
    return f'\nNext review will be in:\n{text}'


async def generate_deck_list_text(deck):
    cards_count = deck.get('cards_count')
    new_cards_count = deck.get('new_cards_count')
    reviews_count = deck.get('reviews_count')
    next_review_date = None
    if cards_count > 0 and reviews_count == 0 and new_cards_count == 0:
        min_review_date = deck.get('min_review_date')
        current_server_time = deck.get('current_time')
        next_review_date = datetime.fromisoformat(min_review_date) - datetime.fromisoformat(current_server_time)
        next_review_date = await data_handler(next_review_date)

    text = f'''
*{f"{re.escape(deck.get('name', '_'))}":<70}* 
{f'>Cards in deck: {cards_count:<60}' if cards_count else f'>_No cards in deck_'}
{f'>New cards for studying:  {new_cards_count}' if new_cards_count else f'>_No cards for studying_'}
{f'>Cards for review: {reviews_count}' if reviews_count else f'>_No cards for review_'}
>{re.escape(next_review_date) if next_review_date else ''}
            '''
    return text


async def create_deck_info(deck):
    cards_count = deck.get('cards_count')
    new_cards_count = deck.get('new_cards_count')
    reviews_count = deck.get('reviews_count')
    next_review_date = None
    if cards_count > 0 and reviews_count == 0 and new_cards_count == 0:
        min_review_date = deck.get('min_review_date')
        current_server_time = deck.get('current_time')
        next_review_date = datetime.fromisoformat(min_review_date) - datetime.fromisoformat(current_server_time)
        next_review_date = await data_handler(next_review_date)

    text = f'''
*{f"{re.escape(deck.get('name', '_'))}":<70}* 
{f'>Cards in deck: {cards_count:<60}' if cards_count else f'>_No cards in deck_'}
{f'>New cards for studying:  {new_cards_count}' if new_cards_count else f'>_No cards for studying_'}
{f'>Cards for review: {reviews_count}' if reviews_count else f'>_No cards for review_'}
>{re.escape(next_review_date) if next_review_date else ''}
            '''
    return text


async def delete_two_messages(callback: CallbackQuery):
    message_id = callback.message.message_id
    chat_id = callback.message.chat.id
    await bot.delete_message(chat_id=chat_id, message_id=message_id - 1)
    await asyncio.sleep(1)
    await callback.message.delete()
    await asyncio.sleep(0.5)


async def get_decks_data(message: Message, state: FSMContext):
    tg_id = state.key.user_id if state else message.from_user.id
    get_decks_url = f'{BASE_URL}/deck/api/v1/manage/{tg_id}/'
    response = await send_request(get_decks_url)
    decks_data = response.get('data')
    status = response.get('status')
    return decks_data, status
