from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.utils import QuickAddCard, \
    get_decks_data

router = Router()
router_quick_addcard_text = Router()


@router.message(F.text == 'Add card quick')
@router.message(Command(commands=['addcardquick']))
async def quick_add_card_command(message: Message, state: FSMContext):
    await state.set_state(QuickAddCard.card)
    text = '<blockquote>(сторона 1)<b>..</b>(сторона 2)\nили (сторона 1)<b>..</b>(сторона 2) <b>..</b>2\n<i>две стороны</i></blockquote>\n'
    await message.answer(text, parse_mode=ParseMode.HTML)

@router.message(QuickAddCard.card)
async def quick_add_card_choose_deck(message: Message, state: FSMContext):
    card = message.text
    card_elements = card.split('..') if '..' in card else card.split(',,')
    params = {}
    elements = len(card_elements)
    if elements in (2, 3):
        if elements == 2:
            side1, side2 = card_elements
            num_sides = '1'
        else:
            side1, side2, num_sides = card_elements
            if not num_sides.isdigit() or num_sides not in ('1', '2'):
                num_sides = '1'

        if any(char.isalnum() for char in side1) and any(char.isalnum() for char in side2):
            decks_data, status = await get_decks_data(message, state)
            card_data = {
                'front_side': side1,
                'back_side': side2,
                'is_two_sides': True if num_sides == '2' else False,
            }
            await state.update_data(card_data)
            if status == 200:
                text = 'Choose a deck from the list below:'
                params = {
                    'parse_mode': ParseMode.MARKDOWN_V2,
                    'reply_markup': await kb.deck_names(decks_data, is_quick_add=True),
                }
            elif status == 204:
                text = 'Deck is empty. Please enter name of new deck'
                await state.set_state(QuickAddCard.deck_create)
            else:
                text = \
                    '🤯🥳 Oops, something went wrong.\nPlease press the REFRESH button or try again later.'

        else:
            text = f'The entered data is incorrect.\nYour data looks like:\n<blockquote><b>Side 1:</b>  {side1}\n<b>Side 2:</b>  {side2}\n<b>How many sides:</b>  {num_sides}</blockquote>\nPlease, try again.'
            params = {'parse_mode': ParseMode.HTML, 'reply_markup': await kb.back()}
    else:
        text = f'The entered data is incorrect.\nYour data looks like:\n<pre>{" ".join(card_elements)}</pre>\nPlease, try again.'
        params = {'parse_mode': ParseMode.HTML, 'reply_markup': await kb.back()}

    await message.answer(text, **params)


@router.message(QuickAddCard.deck_create)
@router.callback_query(F.data.startswith('quick_addcard_deck_name_'))
async def quick_add_card_handler(callback_or_message: CallbackQuery or Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == 'QuickAddCard:deck_create':
        message = callback_or_message
        name = message.text
        telegram_id = state.key.user_id
        data = {
            'name': name,
            'telegram_id': telegram_id,
        }
        url = f'{BASE_URL}/deck/api/v1/manage/'
        response = await send_request(url, method='POST', data=data)
        if response.get('status') == 201:
            slug = response.get('data', {}).get('slug')
        else:
            text = '❌ Something went wrong. The deck was not created. Please try again. ✌'
            await message.answer(text)
            await state.clear()
            await asyncio.sleep(1.5)
            return await decks_list(message, state)
    elif isinstance(callback_or_message, CallbackQuery) and callback_or_message.data.startswith(
            'quick_addcard_deck_name_'):
        message = callback_or_message.message
        slug = callback_or_message.data.split('_')[-1]
        await message.delete()
    else:
        return

    data = await state.get_data()
    data['slug'] = slug
    await card_update_create_handler(message, state=state, card_data=data)