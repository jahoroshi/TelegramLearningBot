import asyncio

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

import app.keyboards as kb
from app.middlewares.locales import i18n, i18n_middleware
from app.requests import send_request
from app.states import StartChooseLanguage
from app.utils import set_user_commands, set_initial_user_language
# from app.utils.middleware import start_tips_middleware
from settings import BASE_URL

_ = i18n.gettext


async def process_start_command(callback_or_message: Message | CallbackQuery, state: FSMContext):
    """
    Processes the start or refresh command.
    """
    message = callback_or_message.message if isinstance(callback_or_message, CallbackQuery) else callback_or_message

    if message.text == _('refresh_command') or any(command in message.text for command in ['/refresh', '/start']):
        current_state = await state.get_state()
        if current_state != 'StartChooseLanguage:active':
            await state.clear()

    await set_user_commands(message)
    await process_to_decks_list(message, state)





async def process_choose_initial_language(message: Message, user_language: str):
    """
    Prompts the user to choose the initial language.
    """
    messages = {
        'ru': 'Нажмите продолжить, если ваш язык русский',
        'en': 'Press continue if your language is English'
    }
    selected_language = 'ru' if user_language == 'ru' else 'en'
    opposite_language = 'en' if selected_language == 'ru' else 'ru'

    # Send the language selection messages
    await message.answer(messages[selected_language], reply_markup=await kb.choose_language(selected_language))
    await asyncio.sleep(1.5)
    await message.answer(messages[opposite_language], reply_markup=await kb.choose_language(opposite_language))


async def process_set_language_callback(callback: CallbackQuery, state: FSMContext):
    """
    Processes the callback query to set the initial user language.
    """
    await callback.answer()
    current_state = await state.get_state()

    # Handle language selection
    if current_state == 'StartChooseLanguage:active':
        language = callback.data.split('_')[-1]
        telegram_id = state.key.user_id
        await state.clear()

        # Set initial user language
        await i18n_middleware.set_locale(telegram_id, language.upper())
        response = await set_initial_user_language(telegram_id, language.upper())
        if response.get('status') != 200:
            await process_to_decks_list(callback, state)
            return

        # Send request to fill the initial deck
        url = f'{BASE_URL}/api/v1/deck/manage/first_filling/{telegram_id}/{language}'
        response = await send_request(url, method='GET')
        if response and response.get('status') == 201:
            await callback.message.answer(_('greeting_after_creating_test_deck'), parse_mode=ParseMode.HTML)
            await asyncio.sleep(5)

            # Navigate to the decks list
            await process_to_decks_list(callback, state)

            # Send the first tip message
            tip_message = await callback.message.answer(_('tip_message_1'), parse_mode=ParseMode.HTML)
            i18n_middleware.tip_mode.last_msg = (tip_message.message_id, telegram_id)
        else:
            await process_to_decks_list(callback, state)
    else:
        await process_start_command(callback, state)


async def process_to_decks_list(callback_or_message: Message | CallbackQuery, state: FSMContext):
    """
    Navigates to the decks list.
    """
    from app.services.deckhub.decklist import handle_decks_list_request
    message = callback_or_message.message if isinstance(callback_or_message, CallbackQuery) else callback_or_message
    await handle_decks_list_request(message, state)


async def process_cmd_a(message: Message, state: FSMContext):
    """
    Sends a formatted text message when the 'a' command is triggered.
    """
    text = '''
        <b>bold</b>, <strong>bold</strong>
        <i>italic</i>, <em>italic</em>
        <u>underline</u>, <ins>underline</ins>
        <s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
        <span class="tg-spoiler">spoiler</span>, <tg-spoiler>spoiler</tg-spoiler>
        <b>bold <i>italic bold <s>italic bold strikethrough <span class="tg-spoiler">italic bold strikethrough spoiler</span></s> <u>underline italic bold</u></i> bold</b>
        <a href="http://www.example.com/">inline URL</a>
        <a href="tg://user?id=123456789">inline mention of a user</a>
        <tg-emoji emoji-id="5368324170671202286">👍</tg-emoji>
        <code>inline fixed-width code</code>
        <pre>pre-formatted fixed-width code block</pre>
        <pre><code class="language-python">pre-formatted fixed-width code block written in the Python programming language</code></pre>
        <blockquote>Block quotation started\nBlock quotation continued\nThe last line of the block quotation</blockquote>
        <blockquote expandable>Expandable block quotation started\nExpandable block quotation continued\nExpandable block quotation continued\nHidden by default part of the block quotation started\nExpandable block quotation continued\nThe last line of the block quotation</blockquote>
    '''
    telegram_id = state.key.user_id
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Перейти", web_app=WebAppInfo(url=f'https://jahoroshi4y.pagekite.me/api/v1/study/web_app/{telegram_id}?mode=new&slug=newsuper')))
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard.as_markup())
