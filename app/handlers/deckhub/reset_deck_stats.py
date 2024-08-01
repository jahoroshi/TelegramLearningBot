import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

import app.keyboards as kb
from app.handlers.deckhub.decklist import decks_list
from app.middlewares.locales import i18n
from app.requests import send_request
from app.services import DeckViewingState
from app.services.states import ResetDeckProgress
from settings import BASE_URL

_ = i18n.gettext
router = Router()


@router.callback_query(F.data.startswith('reset_progress_'))
async def reset_deck_progress_confirm(callback: CallbackQuery, state: FSMContext):
    slug = callback.data.split('_')[-1]
    await state.set_state(ResetDeckProgress.active)
    text = '♻️ Resetting your progress will clear all your study data and return all cards in this deck to their initial state.\nCards will not be removed from the deck.\nResetting only affects the current deck.\n\n❓ Do you want to proceed?'
    await callback.message.edit_text(text, reply_markup=await kb.reset_deck_progress(slug))


@router.callback_query(F.data.startswith('reset_deck_confirm_'))
async def reset_deck_progress_handler(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state == ResetDeckProgress.active:
        slug = callback.data.split('_')[-1]
        telegram_id = state.key.user_id
        url = f'{BASE_URL}/deck/api/v1/manage/reset/{telegram_id}/{slug}/'
        response = await send_request(url, method='GET')
        if response.get('status') == 200:
            text = '♻️ Deck was successfully reset. ♻️\n_'
        elif response.get('status') == 204:
            text = 'Deck is empty.'
        else:
            text = 'Something went wrong.'
        await callback.message.delete_reply_markup()
        await state.set_state(DeckViewingState.active)
        await callback.message.answer(text, reply_markup=kb.refresh_button)
        await asyncio.sleep(2)
    await decks_list(callback.message, state)
