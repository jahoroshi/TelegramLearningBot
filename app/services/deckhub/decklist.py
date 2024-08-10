from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.middlewares.i18n_init import i18n
from app.utils import get_decks_data
from app.states import DeckViewingState
from app.states import ServerError

_ = i18n.gettext

async def handle_decks_list_request(message: Message, state: FSMContext, caller=None):
    """
    Processes the request to retrieve the list of decks and sends appropriate messages to the user.
    """
    decks_data, status = await get_decks_data(message, state)
    deck_title = _('deck_title')
    deck_title_txt = f'📚 <b>{f"<i>{deck_title}</i>":^50}</b> 📚'

    if status == 200:
        # Successful retrieval of deck data
        await state.set_state(DeckViewingState.active)
        text = _('choose_deck_from_list')
        params = {
            'parse_mode': ParseMode.HTML,
            'reply_markup': await kb.deck_names(decks_data),
        }
        if caller == 'from back btn':
            await message.edit_text(f'<b><i>{text}</i></b>\n', **params)
        else:
            await message.answer(
                deck_title_txt,
                parse_mode=ParseMode.HTML,
                reply_markup=await kb.main_button(decks_data)
            )
            await message.answer(text, **params)
    elif status == 204:
        # No decks available
        await message.answer(
            deck_title_txt,
            parse_mode=ParseMode.HTML,
            reply_markup=kb.create_new_deck_button
        )
        text = _('decks_empty_create_new')
        await message.answer(text, reply_markup=await kb.create_new_deck())
    else:
        # Handle errors
        current_state = await state.get_state()
        if current_state == 'ServerError:active':
            text = _('error_occurred_contact_support')
        else:
            text = _('oops_try_again')

        await message.answer(text, reply_markup=kb.refresh_button)
        await state.set_state(ServerError.active)

async def handle_to_decks_list(callback: CallbackQuery, state: FSMContext):
    """
    Processes the callback query to navigate to the list of decks.
    """
    await callback.answer()
    await state.clear()
    await handle_decks_list_request(callback.message, state)

async def handle_back_to_decks_btn(callback: CallbackQuery, state: FSMContext):
    """
    Processes the callback query to return to the list of decks.
    """
    await callback.answer()
    await handle_decks_list_request(callback.message, state, caller='from back btn')
