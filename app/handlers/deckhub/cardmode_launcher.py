from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.handlers.cardmode.cardmode_start import card_mode_start
from app.middlewares.i18n_init import i18n

_ = i18n.gettext
router = Router()


@router.callback_query(F.data.startswith('choose_study_format_'))
@router.message(
    F.text.in_([_(j, locale=i) for i in ('en', 'ru') for j in (_('study_all_decks'), _('review_all_decks'))]))
async def choose_study_format(callback_or_message: CallbackQuery or Message, state: FSMContext):
    text = _('study_format')
    if isinstance(callback_or_message, CallbackQuery):
        slug, study_mode = callback_or_message.data.split('_')[-2:]
        message = callback_or_message.message
        await message.edit_text(text=text, reply_markup=await kb.choose_study_format(slug, study_mode))

    else:
        message = callback_or_message
        slug = 'alldecks'
        telegram_id = state.key.user_id
        study_mode = f'new-{telegram_id}-all' if message.text == _('study_all_decks') else f'review-{telegram_id}-all'

        await message.answer(text=text, reply_markup=await kb.choose_study_format(slug, study_mode))


@router.callback_query(F.data.startswith('start_studying_'))
async def launch_card_mode(callback: CallbackQuery, state: FSMContext):
    slug, study_mode, study_format = callback.data.split('_')[-3:]
    await callback.answer()
    await state.clear()
    await card_mode_start(callback.message, state, slug=slug, study_mode=study_mode, study_format=study_format)
