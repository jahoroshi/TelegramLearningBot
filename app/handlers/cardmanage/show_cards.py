import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove

import app.keyboards as kb
from app.handlers import decks_list
from app.requests import send_request
from app.services import check_current_state, CardManage
from settings import BASE_URL

router = Router()


@router.callback_query(F.data.startswith('show_cards_'))
@check_current_state
async def show_cards(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    slug = callback.data.split('_')[-1]
    tg_id = state.key.user_id
    url = f'{BASE_URL}/deck/api/v1/manage/{tg_id}/{slug}/'
    response = await send_request(url, method='GET')
    status = response.get('status')
    if status == 200:
        data = response.get('data', {})
        cards_list = ''
        card_id_to_row_number = {}
        cur_row_number = 1
        cards_id_index = {}
        data.sort(key=lambda x: x['card_id'])
        for card in data:
            card_id = card['card_id']
            if card_id not in card_id_to_row_number:
                cards_list += f'» {cur_row_number}. {card.get("side1")}  |  {card.get("side2")}\n'
                card_id_to_row_number[card_id] = cur_row_number
                cards_id_index[cur_row_number] = card_id
                cur_row_number += 1
            else:
                cards_list += f'» {card_id_to_row_number[card_id]}. {card.get("side1")}  |  {card.get("side2")}\n'
                cards_id_index[card_id_to_row_number[card_id]] = card_id
        if len(cards_list) != 0:
            await callback.message.edit_text(cards_list, reply_markup=await kb.show_cards_action_buttons(slug))
            await state.set_state(CardManage.card_ops_state)
            await state.update_data(cards_id_index=cards_id_index, slug=slug)
        else:
            await callback.message.edit_text('📂 The deck is empty.',
                                             reply_markup=await kb.back_to_decklist_or_deckdetails(slug))

    else:
        text = '❗️ Something went wrong.'
        await callback.message.answer(text, reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(1.5)
        await decks_list(callback.message, state)