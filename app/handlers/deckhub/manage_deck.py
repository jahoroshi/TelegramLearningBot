from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

import app.keyboards as kb
from app.middlewares.i18n_init import i18n

_ = i18n.gettext
router = Router()


@router.callback_query(F.data.startswith('manage_deck_edit_del_'))
async def manage_deck_edit_del_reset(callback: CallbackQuery, state: FSMContext):
    slug = callback.data.split('_')[-1]
    await callback.message.edit_reply_markup(reply_markup=await kb.manage_deck_edit_del_res(slug))
