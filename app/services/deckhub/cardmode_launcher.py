from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.services.cardmode.cardmode_start import process_card_mode_start
from app.middlewares.i18n_init import i18n

_ = i18n.gettext

async def process_choose_study_client(callback_or_message: CallbackQuery or Message, state: FSMContext):

    text = _('choose_study_client')

    if isinstance(callback_or_message, CallbackQuery):
        slug, study_mode = callback_or_message.data.split('_')[-2:]
        message = callback_or_message.message
        await message.edit_text(text=text, reply_markup=await kb.choose_study_client(slug, study_mode), parse_mode=ParseMode.HTML)

    else:
        message = callback_or_message
        slug = 'alldecks'
        telegram_id = state.key.user_id
        study_mode = f'new-{telegram_id}-all' if message.text == _('study_all_decks') else f'review-{telegram_id}-all'

        await message.answer(text=text, reply_markup=await kb.choose_study_client(slug, study_mode), parse_mode=ParseMode.HTML)

async def process_choose_study_format(callback: CallbackQuery, state: FSMContext):

    text = _('study_format')


    slug, study_mode, client = callback.data.split('_')[-3:]
    if client == 'webapp':
        telegram_id = state.key.user_id
        study_client = {'web_app': telegram_id}
    else:
        study_client = {'chat': None}

    message = callback.message
    await message.edit_text(text=text, reply_markup=await kb.choose_study_format(slug, study_mode, study_client))



async def process_launch_card_mode(callback: CallbackQuery, state: FSMContext):
    """
    Processes the initiation of the card mode session based on the user's selections.

    Args:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The finite state machine context for the user.
    """
    slug, study_mode, study_format = callback.data.split('_')[-3:]
    await callback.answer()
    await state.clear()

    # Start the card mode session with the selected parameters
    await process_card_mode_start(callback.message, state, slug=slug, study_mode=study_mode, study_format=study_format)
