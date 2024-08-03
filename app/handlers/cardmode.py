from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from typing import Optional

import app.keyboards as kb
from app.middlewares.i18n_init import i18n
from app.services.cardmode import (
    process_show_first_letters,
    process_scramble_letters,
    process_scramble_letters_check,
    process_show_similar,
    process_similar_answer_check,
    process_set_rating,
    process_card_already_known,
    process_show_back,
    process_card_mode_start,
    process_card_mode,
    process_text_to_speech,
)
from app.utils.decorators import check_card_data

# Initialize router
router = Router()

# Define gettext
_ = i18n.gettext

### Card Mode Handlers ###

async def card_mode_start(message: Message, state: FSMContext, slug: Optional[str] = None,
                          study_mode: Optional[str] = None, study_format: Optional[str] = None):
    """
    Handler to start the card mode session for studying.
    """
    await process_card_mode_start(message, state, slug, study_mode, study_format)

### Show First Letters Handler ###

@router.callback_query(F.data.startswith('button_show_first_letters'))
@check_card_data
async def show_first_letters(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    """
    Handler to show the first letters of the card's back side.

    This handler is triggered by a callback query when the user requests to see the first few letters of the card's back side.
    """
    await process_show_first_letters(callback, state, data_store)

### Scramble Letters Handlers ###

@router.callback_query(F.data == 'button_scramble_letters')
@check_card_data
async def scramble_letters(callback: CallbackQuery, state: FSMContext, data_store: dict = None,
                           scrambled_segment: str = None, guessed_segment: str = None, is_sentence: bool = None):
    """
    Handler to initiate the letter scrambling process for a card's back side.
    """
    await process_scramble_letters(callback, state, data_store, scrambled_segment, guessed_segment, is_sentence)


@router.callback_query(F.data.startswith('scramble_'))
@check_card_data
async def scramble_letters_check(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    """
    Handler to check the user's answer against the scrambled letters.
    """
    await process_scramble_letters_check(callback, state, data_store)

### Show Similar Words Handlers ###

@router.callback_query(F.data == 'button_show_similar')
@check_card_data
async def show_similar(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    """
    Handler for showing similar words to the card's back side.
    """
    await process_show_similar(callback, state, data_store)


@router.callback_query(F.data.startswith('similar_'))
@check_card_data
async def similar_answer_check(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    """
    Handler for checking the user's answer against similar words.
    """
    await process_similar_answer_check(callback, state, data_store)

### Set Rating Handler ###

@router.message(F.text.in_([_(j, locale=i) for i in ('en', 'ru') for j in ("again", "good", "hard", "easy")]))
@check_card_data
async def set_rating(message: Message, state: FSMContext, data_store: dict = None, rating=None):
    """
    Handler for setting the rating of a card based on user feedback.

    This handler is triggered when the user rates the difficulty of a card.
    """
    await process_set_rating(message, state, data_store, rating)

### Card Already Known Handler ###

@router.callback_query(F.data == 'card_is_already_known')
async def card_is_already_known(callback: CallbackQuery, state: FSMContext):
    """
    Handler for marking the card as already known.

    This handler is triggered when the user indicates that they already know the card.
    """
    await process_card_already_known(callback, state)

### Show Back Handler ###

@router.callback_query(F.data == 'button_show_back')
@check_card_data
async def show_back(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    """
    Handler for showing the back side of the card.

    This handler is triggered when the user requests to see the back side of the card.
    """
    await process_show_back(callback, state, data_store)


### Text to Speech Handler ###

@router.callback_query(F.data.in_(('button_speech', 'button_speech_locked')))
@check_card_data
async def text_to_speech(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    """
    Handler to convert text to speech for a card's front side.

    This handler is triggered when the user requests to hear the text-to-speech conversion of the card.
    """
    await process_text_to_speech(callback, state, data_store)
