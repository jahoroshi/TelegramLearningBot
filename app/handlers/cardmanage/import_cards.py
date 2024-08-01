from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.requests import send_request
from app.services import check_current_state, ImportCards
from settings import BASE_URL

router = Router()

@router.callback_query(F.data.startswith('import_cards_'))
@check_current_state
async def import_cards(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(ImportCards.data)
    slug = callback.data.split('_')[-1]
    await state.update_data(slug=slug)
    await callback.message.edit_text(
        f'''🔔 *Import instruction:*
» Max lenght message 4096 chars\.\n
» Use semicolon * \; * as separator between sides\n
» Each card must be on a new line\.

*Example\:*
>\(_front side_\) *\;* \(_back side_\)
>{f"Apple":^14} *\;* {f"Яблоко":^11}
>{f"Orange":^12} *\;* {f"Апельсин":^11}

_enter text or press back for cansel_
''', parse_mode=ParseMode.MARKDOWN_V2, reply_markup=await kb.back_to_decklist_or_deckdetails(slug))


@router.message(ImportCards.data)
async def import_cards_handler(message: Message, state: FSMContext):
    cards = message.text
    data = await state.get_data()
    slug = data.get('slug')
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
    if status == 201:
        text = response.get('data', {}).get('detail')
    else:
        text = '❗️ Something went wrong.'
    await message.answer(text, reply_markup=await kb.back_to_decklist_or_deckdetails(slug))
    # await asyncio.sleep(1)
    # await decks_list(message, state)