from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

import app.keyboards as kb


async def process_manage_deck_edit_del_reset(callback: CallbackQuery, state: FSMContext):
    """
    Processes the management of deck edit/delete/reset options.

    Args:
        callback (CallbackQuery): The callback query from the user.
        state (FSMContext): The finite state machine context for the user.
    """
    slug = callback.data.split('_')[-1]

    # Update the message with management options for the selected deck
    await callback.message.edit_reply_markup(reply_markup=await kb.manage_deck_edit_del_res(slug))
