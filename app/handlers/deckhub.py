import asyncio
from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from app.middlewares.i18n_init import i18n
from app.services.deckhub import (
    handle_decks_list_request,
    handle_to_decks_list,
    handle_back_to_decks_btn,
    process_deck_create,
    process_deck_create_handler,
    process_deck_details,
    process_delete_deck_confirm,
    process_deck_delete,
    process_manage_deck_edit_del_reset,
    process_rename_deck,
    process_rename_deck_handler,
    process_reset_deck_progress_confirm,
    process_reset_deck_progress_handler,
)
from app.services.deckhub import (
    process_choose_study_format,
    process_launch_card_mode,
)
from app.states import DeckCreate, DeckRename
from app.utils import clear_current_state, check_current_state

# Initialize router
router = Router()

# Define gettext
_ = i18n.gettext

### Deck List Handlers ###

@router.message(Command('back'))
async def decks_list(message: Message, state: FSMContext):
    """
    Handler for the 'back' command that calls the business logic to display the list of decks.
    """
    await state.clear()
    await handle_decks_list_request(message, state)


@router.callback_query(F.data == 'to_decks_list')
async def to_decks_list(callback: CallbackQuery, state: FSMContext):
    """
    Callback handler to navigate to the list of decks.
    """
    await state.clear()
    await handle_to_decks_list(callback, state)


@router.callback_query(F.data == 'back_to_decks')
async def back_to_decks_btn(callback: CallbackQuery, state: FSMContext):
    """
    Callback handler to return to the list of decks.
    """
    await state.clear()
    await handle_back_to_decks_btn(callback, state)

### Study Format Handlers ###

@router.callback_query(F.data.startswith('choose_study_format_'))
@router.message(
    F.text.in_([_(j, locale=i) for i in ('en', 'ru') for j in ('study_all_decks', 'review_all_decks')])
)
async def choose_study_format(callback_or_message: CallbackQuery or Message, state: FSMContext):
    """
    Handler for choosing the study format.

    This handler is triggered when the user selects a study or review option.
    """
    await process_choose_study_format(callback_or_message, state)


@router.callback_query(F.data.startswith('start_studying_'))
async def launch_card_mode(callback: CallbackQuery, state: FSMContext):
    """
    Handler to launch the card mode for studying.

    This handler is triggered when the user selects to start studying.
    """
    await process_launch_card_mode(callback, state)

### Deck Creation Handlers ###

@router.message(Command(commands=['newdeck']))
@router.message(F.text == 'Create deck')
@router.callback_query(F.data == 'deck_create')
async def deck_create(callback_or_message: CallbackQuery or Message, state: FSMContext):
    """
    Handler to initiate the deck creation process.

    This handler is triggered by the `/newdeck` command, the 'Create deck' text, or the 'deck_create' callback query.
    """
    await process_deck_create(callback_or_message, state)


@router.message(DeckCreate.name)
async def deck_create_handler(message: Message, state: FSMContext):
    """
    Handler to finalize the deck creation process after the deck name is provided.

    This handler is triggered when the user provides a deck name.
    """
    await process_deck_create_handler(message, state)

### Deck Details Handler ###

@router.callback_query(F.data.startswith('deck_details_'))
@clear_current_state
async def deck_details(callback_or_message: CallbackQuery or Message, state: FSMContext, slug=None):
    """
    Handler for displaying deck details.

    This handler is triggered when a user selects a deck to view its details.
    """
    await process_deck_details(callback_or_message, state, slug)

### Deck Deletion Handlers ###

@router.callback_query(F.data.startswith('delete_deck_'))
@check_current_state
async def delete_deck_confirm(callback: CallbackQuery, state: FSMContext):
    """
    Handler to confirm the deletion of a deck.

    This handler is triggered when a user selects to delete a deck.
    """
    await process_delete_deck_confirm(callback, state)


@router.callback_query(F.data.startswith('confirm_delete_deck_'))
async def deck_delete(callback: CallbackQuery, state: FSMContext):
    """
    Handler to perform the deck deletion.

    This handler is triggered when a user confirms the deletion of a deck.
    """
    await process_deck_delete(callback, state)

### Deck Management Handler ###

@router.callback_query(F.data.startswith('manage_deck_edit_del_'))
async def manage_deck_edit_del_reset(callback: CallbackQuery, state: FSMContext):
    """
    Handler for managing deck edit/delete/reset options.

    This handler is triggered when a user selects an option to manage a deck.
    """
    await process_manage_deck_edit_del_reset(callback, state)

### Deck Renaming Handlers ###

@router.callback_query(F.data.startswith('rename_deck_'))
@check_current_state
async def rename_deck(callback: CallbackQuery, state: FSMContext):
    """
    Handler to initiate the deck renaming process.

    This handler is triggered when a user selects the option to rename a deck.
    """
    await process_rename_deck(callback, state)


@router.message(DeckRename.new_name)
async def rename_deck_handler(message: Message, state: FSMContext):
    """
    Handler to finalize the deck renaming process after receiving the new name.

    This handler is triggered when the user provides a new name for the deck.
    """
    await process_rename_deck_handler(message, state)

### Deck Progress Reset Handlers ###

@router.callback_query(F.data.startswith('reset_progress_'))
async def reset_deck_progress_confirm(callback: CallbackQuery, state: FSMContext):
    """
    Handler to confirm the reset of deck progress.

    This handler is triggered when a user selects the option to reset a deck's progress.
    """
    await process_reset_deck_progress_confirm(callback, state)


@router.callback_query(F.data.startswith('reset_deck_confirm_'))
async def reset_deck_progress_handler(callback: CallbackQuery, state: FSMContext):
    """
    Handler to execute the reset of deck progress.

    This handler is triggered when a user confirms the reset of a deck's progress.
    """
    await process_reset_deck_progress_handler(callback, state)
