import asyncio
from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.middlewares.i18n_init import i18n
from app.requests import send_request
from bot import bot
from settings import BASE_URL

_ = i18n.gettext


async def data_handler(data):
    days = data.days
    hours, remainder = divmod(data.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if days:
        text = _('{days}d : {hours}h : {minutes} min').format(days=days, hours=hours, minutes=minutes)
    else:
        text = _('{hours}h : {minutes}min').format(hours=hours, minutes=minutes)
    return _('\nNext review will be in:\n{text}').format(text=text)


async def create_deck_info(deck):
    cards_count = deck.get('cards_count')
    new_cards_count = deck.get('new_cards_count')
    reviews_count = deck.get('reviews_count')
    next_review_date = None
    deck_name = deck.get('name', '_')
    deck_name = deck_name.replace("<", "&lt;").replace(">", "&gt;")
    if cards_count > 0 and reviews_count == 0 and new_cards_count == 0:
        min_review_date = deck.get('min_review_date')
        current_server_time = deck.get('current_time')
        next_review_date = datetime.fromisoformat(min_review_date) - datetime.fromisoformat(current_server_time)
        next_review_date = await data_handler(next_review_date)

    text = _(
        '''
<b>{deck_name:<70}</b> 
<blockquote>{cards_count_text}
{new_cards_text}
{reviews_text}
{next_review_text}</blockquote>
        ''').format(
        deck_name=f"{deck_name}",
        cards_count_text=f'{_("cards_in_deck")}: {cards_count:<60}' if cards_count else f'<i>{_("no_cards_in_deck")}</i>',
        new_cards_text=f'{_("new_cards_for_studying")}:  {new_cards_count}' if new_cards_count else f'<i>{_("no_new_cards_for_studying")}</i>',
        reviews_text=f'{_("cards_for_review")}: {reviews_count}' if reviews_count else f'<i>{_("no_cards_for_review")}</i>',
        next_review_text=next_review_date if next_review_date else ''
    )
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
