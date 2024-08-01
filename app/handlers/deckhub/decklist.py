from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.middlewares.locales import i18n
from app.services import DeckViewingState, get_decks_data
from app.services.states import ServerError

_ = i18n.gettext
router = Router()


@router.message(F.text.in_(('Decks', 'Back to desks list')))
@router.message(Command('back'))
async def decks_list(message: Message, state: FSMContext, caller=None):
    decks_data, status = await get_decks_data(message, state)
    if status == 200:
        await state.set_state(DeckViewingState.active)
        text = 'Choose a deck from the list below:'
        params = {
            'parse_mode': ParseMode.MARKDOWN_V2,
            'reply_markup': await kb.deck_names(decks_data),
        }
        if caller == 'from back btn':
            await message.edit_text(text, **params)
        else:
            deck_title = i18n.gettext('decks')
            await message.answer(f'📂 *{f"__{deck_title}__":^50}* 📂', parse_mode=ParseMode.MARKDOWN_V2,
                                 reply_markup=await kb.main_button(decks_data))
            await message.answer(text, **params)

        # await message.answer(text, parse_mode=ParseMode.MARKDOWN_V2,
        #                      reply_markup=await kb.deck_names(response.get('data')))
    elif status == 204:
        deck_title = i18n.gettext('decks')
        await message.answer(f'🗃 *{f"__{deck_title}__":^50}* 🗃', parse_mode=ParseMode.MARKDOWN_V2,
                             reply_markup=kb.create_new_deck_button)
        text = 'Decks is empty. Please, create a new deck.'
        await message.answer(text, reply_markup=await kb.create_new_deck())
    else:
        current_state = await state.get_state()
        if current_state == 'ServerError:active':
            text = ("🤯🥳 An error occurred "
                    "\nIf this issue continues, please contact us through our help center at ankichat.com.")
        else:
            text = \
                '🤯🥳 Oops, something went wrong.\nPlease press the REFRESH button or try again later.'

        await message.answer(text, reply_markup=kb.refresh_button)
        await state.set_state(ServerError.active)


@router.callback_query(F.data == 'to_decks_list')
async def to_decks_list(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await decks_list(callback.message, state)


@router.callback_query(F.data == 'back_to_decks')
async def back_to_decks_btn(callback: CallbackQuery, state: FSMContext):
    # await state.clear()
    await callback.answer()
    await decks_list(callback.message, state, caller='from back btn')