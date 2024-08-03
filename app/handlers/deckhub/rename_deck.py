from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.middlewares.i18n_init import i18n
from app.requests import send_request
from app.utils import check_current_state, DeckViewingState, DeckRename
from settings import BASE_URL

_ = i18n.gettext
router = Router()


@router.callback_query(F.data.startswith('rename_deck_'))
@check_current_state
async def rename_deck(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    slug = callback.data.split('_')[-1]
    await state.set_state(DeckRename.new_name)
    await state.update_data(slug=slug)
    # await callback.message.edit_reply_markup(reply_markup=await kb.back())
    await callback.message.answer(
        _('enter_new_deck_name'),
        parse_mode=ParseMode.MARKDOWN_V2
    )


@router.message(DeckRename.new_name)
async def rename_deck_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    new_name = message.text
    if len(new_name) > 100:
        text = _('max_100_chars')
        return await message.answer(text)
        # return await display_message_and_redirect(message, state, text)

    if new_name and any(char.isalnum() for char in new_name):
        new_name = new_name.capitalize().strip()
        slug = data.get('slug')
        url = f'{BASE_URL}/deck/api/v1/manage/{slug}/'
        response = await send_request(url, method='PUT', data={'name': new_name})
        status = response.get('status', 0)
        if status // 100 == 2:
            text = _('deck_name_changed')
            slug = response.get('data', {}).get('slug')
        else:
            text = _('something_went_wrong')
        await state.set_state(DeckViewingState.active)
        await message.answer(text, reply_markup=await kb.back_to_decklist_or_deckdetails(slug))
    else:
        text = _('name_letters_numbers')
        await message.answer(text)
    # await deck_info(message, state, slug)
    # await display_message_and_redirect(message, state, text)
