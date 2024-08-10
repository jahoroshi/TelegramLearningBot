from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.middlewares.i18n_init import i18n
from app.services.cardmanage import (
    begin_quick_card_create,
    handle_command_card_create,
    begin_card_create_callback,
    handle_card_update_delete_callback,
    handle_card_delete,
    handle_card_update,
    handle_card_sides_input,
    process_card_update_create_handler,
    process_card_create_get_slug,
    process_import_cards,
    process_import_cards_handler,
    process_show_cards,
    process_show_cards_with_pagination,
)
from app.states import CardManage, ImportCards
from app.utils import check_current_state

# Initialize routers
router = Router()
router_quick_card_create = Router()

# Define gettext
_ = i18n.gettext


### Quick Card Creation Handlers ###

@router_quick_card_create.message()
async def quick_card_create_begin(message: Message, state: FSMContext):
    """
    Handler to begin the quick card creation process.
    """
    current_state = await state.get_state()
    if current_state != 'StartChooseLanguage:active':
        await begin_quick_card_create(message, state)


### Card Creation Handlers ###

@router.message(Command(commands=['addcard']))
async def command_card_create_begin(message: Message, state: FSMContext):
    """
    Handler for the '/addcard' command to begin card creation.
    """
    await handle_command_card_create(message, state)


@router.callback_query(F.data.startswith('add_card_'))
@check_current_state
async def card_create_begin(callback: CallbackQuery, state: FSMContext):
    """
    Callback handler to begin card creation from a deck.
    """
    await begin_card_create_callback(callback, state)


### Card Update/Delete Handlers ###

@router.callback_query(F.data.startswith('edit_card_'))
@router.callback_query(F.data.startswith('delete_card_'))
@check_current_state
async def card_update_delete_begin(callback: CallbackQuery, state: FSMContext):
    """
    Callback handler to begin the card update or delete process.
    """
    await handle_card_update_delete_callback(callback, state)


@router.message(CardManage.del_list_index)
async def card_delete_getting_id(message: Message, state: FSMContext):
    """
    Handler to get the card ID for deletion.
    """
    await handle_card_delete(message, state)


@router.message(CardManage.upd_list_index)
async def card_update_getting_id(message: Message, state: FSMContext):
    """
    Handler to get the card ID for updating.
    """
    await handle_card_update(message, state)


@router.message(CardManage.front_side)
@router.message(CardManage.back_side)
async def card_update_create_enter_sides(message: Message, state: FSMContext, side1: str = None):
    """
    Handler to enter the front and back sides of the card during creation or update.
    """
    await handle_card_sides_input(message, state, side1)


@router.callback_query(F.data.startswith(('is_two_sides', 'is_one_side', 'addcard_slug_')))
@check_current_state
async def card_update_create_handler(callback: CallbackQuery, state: FSMContext, card_data=None):
    """
    Callback handler for card update and creation actions.
    """
    await process_card_update_create_handler(callback, state)





### Card Import Handlers ###

@router.callback_query(F.data.startswith('import_cards_'))
@check_current_state
async def import_cards(callback: CallbackQuery, state: FSMContext):
    """
    Handler for starting the card import process.
    """
    await process_import_cards(callback, state)


@router.message(ImportCards.data)
async def import_cards_handler(message: Message, state: FSMContext):
    """
    Handler for processing the card import data provided by the user.
    """
    await process_import_cards_handler(message, state)


### Show Cards Handler ###

@router.callback_query(F.data.startswith('show_cards_'))
@check_current_state
async def show_cards(callback: CallbackQuery, state: FSMContext):
    """
    Handler for showing cards in a deck.
    """
    await process_show_cards(callback, state)



@router.callback_query(F.data.startswith('show_card_pag_'))
@check_current_state
async def show_cards_with_pagination(callback: CallbackQuery, state: FSMContext):
    """
    Handler for showing cards in a deck.
    """
    await process_show_cards_with_pagination(callback, state)