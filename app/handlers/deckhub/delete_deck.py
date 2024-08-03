import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

import app.keyboards as kb
from app.handlers.deckhub.decklist import decks_list
from app.middlewares.i18n_init import i18n
from app.requests import send_request
from app.utils import check_current_state, DeckViewingState, DeckDelete, delete_two_messages
from settings import BASE_URL

_ = i18n.gettext
router = Router()


@router.callback_query(F.data.startswith('delete_deck_'))
@check_current_state
async def delete_deck_confirm(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(DeckDelete.active)
    slug = callback.data.split('_')[-1]
    text = _('confirm_delete_deck')
    await callback.message.delete_reply_markup()
    await callback.message.answer(text, reply_markup=await kb.confirm_delete_desk(slug))


@router.callback_query(F.data.startswith('confirm_delete_deck_'))
async def deck_delete(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    await callback.answer()
    if current_state == DeckDelete.active:
        slug = callback.data.split('_')[-1]
        url = f'{BASE_URL}/deck/api/v1/manage/{slug}/'
        response = await send_request(url, method='DELETE')
        if response.get('status') == 204:
            text = _('deck_deleted')
            await delete_two_messages(callback)
        else:
            text = _('something_went_wrong')
            await callback.message.delete_reply_markup()
        await state.set_state(DeckViewingState.active)
        await callback.message.answer(text, reply_markup=kb.refresh_button)
        await asyncio.sleep(1.5)
    await decks_list(callback.message, state)
