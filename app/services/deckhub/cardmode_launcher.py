from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.services.cardmode.cardmode_start import process_card_mode_start
from app.middlewares.i18n_init import i18n

_ = i18n.gettext


async def process_choose_study_format(callback_or_message: CallbackQuery or Message, state: FSMContext):
    """
    Processes the user's choice of study format and updates the message or sends a new message accordingly.

    Args:
        callback_or_message (CallbackQuery or Message): The callback query or message object from the user.
        state (FSMContext): The finite state machine context for the user.
    """
    text = _('study_format')

    # Check if the input is a callback query
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
