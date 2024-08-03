from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.middlewares.i18n_init import i18n
from app.utils import DeckViewingState, get_decks_data
from app.utils.states import ServerError

_ = i18n.gettext
router = Router()


# @router.message(F.text.in_((_('decks'), _('back_to_decks_list'))))
@router.message(Command('back'))
async def decks_list(message: Message, state: FSMContext, caller=None):
    decks_data, status = await get_decks_data(message, state)
    deck_title = _('deck_title')
    deck_title_txt = f'🗃 <b>{f"<i>{deck_title}</i>":^50}</b> 🗃'
    if status == 200:
        await state.set_state(DeckViewingState.active)
        text = _('choose_deck_from_list')
        params = {
            'parse_mode': ParseMode.HTML,
            'reply_markup': await kb.deck_names(decks_data),
        }
        if caller == 'from back btn':
            await message.edit_text(f'{deck_title_txt}\n{text}', **params)
        else:

            await message.answer(deck_title_txt,
                                 parse_mode=ParseMode.HTML,
                                 reply_markup=await kb.main_button(decks_data)
                                 )
            await message.answer(text, **params)

        # await message.answer(text, parse_mode=ParseMode.MARKDOWN_V2,
        #                      reply_markup=await kb.deck_names(response.get('data')))
    elif status == 204:
        await message.answer(deck_title_txt,
                             parse_mode=ParseMode.HTML,
                             reply_markup=kb.create_new_deck_button
                             )
        text = _('decks_empty_create_new')
        await message.answer(text, reply_markup=await kb.create_new_deck())
    else:
        current_state = await state.get_state()
        if current_state == 'ServerError:active':
            text = _('error_occurred_contact_support')
        else:
            text = _('oops_try_again')

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
