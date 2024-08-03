from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.middlewares.i18n_init import i18n
from app.requests import send_request
from app.states import ImportCards
from settings import BASE_URL

_ = i18n.gettext


async def process_import_cards(callback: CallbackQuery, state: FSMContext):
    """
    Processes the import cards command by setting the state and updating data.
    """
    await callback.answer()
    await state.set_state(ImportCards.data)
    slug = callback.data.split('_')[-1]
    await state.update_data(slug=slug)

    # Edit the message to show import instructions
    instruction_text = _('import_instruction')
    await callback.message.edit_text(f'{instruction_text}',
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=await kb.back_to_decklist_or_deckdetails(slug)
                                     )


async def process_import_cards_handler(message: Message, state: FSMContext):
    """
    Handles the import of card data when the user submits card text.
    """
    cards = message.text
    data = await state.get_data()
    slug = data.get('slug')

    # Prepare card import data
    cards_data = {
        'text': cards,
        'cards_separator': 'new_line',
        'words_separator': 'semicolon',
        'words_separator_custom': '',
        'cards_separator_custom': '',
    }

    url = f'{BASE_URL}/cards/api/v1/import_cards/{slug}/'
    response = await send_request(url, method='POST', data=cards_data)
    status = response.get('status')

    # Determine the response message based on status
    if status == 201:
        detail = response.get('data', {}).get('detail', ' ')
        success_count = detail.split()[0]
        text = _('cards_imported_successfully').format(success_count)
    else:
        text = _('something_went_wrong')

    await message.answer(text, reply_markup=await kb.back_to_decklist_or_deckdetails(slug))
