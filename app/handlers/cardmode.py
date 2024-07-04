import functools
from typing import Optional

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import BufferedInputFile
from aiogram.types import Message, CallbackQuery
from pydantic import ValidationError

import app.database.requests as rq
import app.keyboards as kb
from app.middlewares import TestMiddleware
from app.requests import send_request
from app.services.handlers import generate_output_text
from app.validators import StartConfigValidator, card_data_isvalid
from settings import BASE_URL

router = Router()

router.message.outer_middleware(TestMiddleware())


class Reg(StatesGroup):
    name = State()
    number = State()


class CardMode(StatesGroup):
    show_first_letters = State()


def check_card_data(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if isinstance(args[0], CallbackQuery):
            msg = args[0].message
        elif isinstance(args[0], Message):
            msg = args[0]
        else:
            print('Firs argument must by CallbackQuery or Message')
            return
        tg_user_id = args[0].from_user.id
        state: FSMContext = kwargs.get('state')
        data_store = await state.get_data()
        card_data = data_store.get('card_data')
        kwargs['data_store'] = data_store
        if card_data is None:
            await card_mode_start(message=msg, state=state, tg_user_id=tg_user_id)
            return
        # filtered_kwargs = {k: v for k, v in kwargs.items() if k in func.__annotations__}
        return await func(*args, **kwargs)
        # return await func(*args, state=state, data_store=data_store)

    return wrapper


async def send_message_card_mode(message: Message, buttons_to_show: dict, text: str):
    await message.answer(
        text=f'{text}',
        reply_markup=await kb.card_mode_buttons(buttons_to_show)
    )


@router.message(CommandStart())
@router.callback_query(F.data == 'to_main')
async def cmd_start(message: Message, state: FSMContext,):
    if isinstance(message, Message):
        await message.answer('Добро пожаловать', reply_markup=kb.studying_start)
    else:
        await state.clear()
        await message.message.answer('Добро пожаловать', reply_markup=kb.studying_start)



@router.message(F.text == 'Start studying')
async def card_mode_start(message: Message, state: FSMContext, slug: Optional[str] = None,
                          study_mode: Optional[str] = None, tg_user_id: Optional[int] = None):
    tg_id = message.from_user.id if tg_user_id is None else tg_user_id
    data_store = await state.get_data()
    try:
        StartConfigValidator(**data_store.get('start_config', {}))
    except ValidationError:
        try:
            if not slug and not study_mode:
                start_url = f'http://localhost:8000/study/api/v1/get_start_config/{tg_id}/'
            else:
                slug = 'qqq'
                study_mode = 'new'
                start_url = f'http://localhost:8000/study/api/v1/get_start_config/{slug}/{study_mode}/{tg_id}/'

            start_config = await send_request(start_url)
            StartConfigValidator(**start_config if start_config else {})
            await state.update_data(start_config=start_config)
        except ValidationError:
            print(f"Validation error after fetching new config in {__name__}")
            await message.answer('Something went wrong, try again.')
            await cmd_start(message)
            return

    await message.answer("Let's begin", reply_markup=await kb.mem_ratings())
    await card_mode(message=message, state=state)


async def card_mode(message: Message, state: FSMContext, card_data: dict = None):
    data_store = await state.get_data()
    text_hint = "_Press 'Show Back' or choose a hint_" if card_data is None else ''

    if not card_data:
        url_get_card = data_store.get('start_config', {}).get('urls', {}).get('get_card')
        if url_get_card:
            card_data = await send_request(f'{BASE_URL}{url_get_card}')
        else:
            await card_mode_start(message=message, state=state)

    if not card_data_isvalid(card_data):
        await message.answer('Something went wrong, try again.')
        await cmd_start(message)

    await state.update_data(card_data=card_data)

    buttons_to_show = data_store['start_config']['buttons_to_show']
    front_side = card_data.get("front_side")
    text = generate_output_text(front=front_side, extra_text=text_hint)

    await message.answer(text, reply_markup=await kb.card_mode_buttons(buttons_to_show),
                         parse_mode=ParseMode.MARKDOWN_V2)


@router.message(F.text.in_({'Again', 'Good', 'Hard', 'Easy'}))
@check_card_data
async def rating_again(message: Message, state: FSMContext, data_store: dict = None):
    ratings = {'Again': 1,
               'Good': 2,
               'Hard': 3,
               'Easy': 4,
               }
    text = message.text
    rating = ratings[text]

    mappings_id = data_store.get('card_data', {}).get('mappings_id')
    url_get_card = data_store.get('start_config', {}).get('urls', {}).get('get_card')
    requests_data = {
        'mappings_id': mappings_id,
        'rating': rating,
    }
    new_card_data = await send_request(f"{BASE_URL}{url_get_card}", method='POST', data=requests_data)
    await card_mode(message, state, card_data=new_card_data)


@router.callback_query(F.data == 'button_show_back')
@check_card_data
async def show_back(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    card_data = data_store.get('card_data')
    text = generate_output_text(card_data=card_data)
    await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN_V2)


@router.callback_query(F.data == 'button_show_similar')
@check_card_data
async def show_similar(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    card_data = data_store.get('card_data')
    url_similar_words = data_store.get('start_config', {}).get('urls', {}).get('get_similar_words', '')
    mappings_id = card_data.get('mappings_id', '')
    url = url_similar_words.replace('dummy_mappings_id', str(mappings_id))
    similar_words_data = await send_request(f"{BASE_URL}{url}")
    if isinstance(similar_words_data, dict) and similar_words_data.get('similar_words'):
        front_side = card_data.get("front_side")
        text = generate_output_text(front=front_side)
        await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN_V2,
                                         reply_markup=await kb.similar_words_output(similar_words_data))
    else:
        await callback.answer('🤯🥳 Similar words not found. Please try again.')


# @router.callback_query(F.data == 'button_show_similar3')
# @check_card_data
# async def show_similar_quiz(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
#     card_data = data_store.get('card_data')
#     url_similar_words = data_store.get('start_config', {}).get('urls', {}).get('get_similar_words', '')
#     mappings_id = card_data.get('mappings_id', '')
#     url = url_similar_words.replace('dummy_mappings_id', str(mappings_id))
#     similar_words_data = await send_request(f"{BASE_URL}{url}")
#     if isinstance(similar_words_data, dict) and (options := similar_words_data.get('similar_words')):
#         front_side = card_data.get("front_side")
#         back_side = card_data.get("back_side")
#         await callback.message.delete()
#         await bot.send_poll(
#             chat_id=callback.message.chat.id,
#             question=front_side,
#             options=options,
#             is_anonymous=False,  # Опрос будет анонимным
#             type='quiz',  # Тип опроса: обычный (regular) или викторина (quiz)
#             allows_multiple_answers=False,  # Разрешить несколько ответов
#             open_period=600,  # Опрос будет активен в течение 600 секунд (10 минут)
#             # explanation="Это вопрос для тестирования опроса",  # Объяснение (только для викторин)
#             # explanation_entities=[],  # Специальные сущности в объяснении (опционально)
#             correct_option_id=sum(index for index, val in enumerate(options) if val == back_side)
#             # Индекс правильного ответа (только для викторин)
#         )
#     else:
#         await callback.answer('🤯🥳 Similar words not found. Please try again.')


@router.callback_query(F.data.startswith('similar_'))
@check_card_data
async def similar_answer_check(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    card_data = data_store.get('card_data')
    user_answer = callback.data.split('_')[1]
    right_answer = card_data.get("back_side")
    if user_answer == 'correct':
        await callback.message.delete()
        extra_text = '🎉 Correct\!'
        text = generate_output_text(card_data=card_data, extra_text=extra_text)
        await callback.message.answer(text, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        text = generate_output_text(front=card_data.get("front_side"))
        await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN_V2)
        await callback.message.answer('The correct answer is 🫴 {} 👈'.format(right_answer))


@router.callback_query(F.data == 'button_scramble_letters')
@check_card_data
async def scramble_letters(callback: CallbackQuery, state: FSMContext, data_store: dict = None,
                           scrambled_segment: str = None, guessed_segment: str = None, is_sentence: bool = None):
    if is_sentence is None:
        back_side = data_store.get('card_data', {}).get('back_side')
        is_sentence = len(elements := back_side.split()) > 3
        scrambled_segment = ' '.join(elements) if not is_sentence else elements
    elements_count = {el: scrambled_segment.count(el) for el in scrambled_segment}

    data = {
        'guessed_segment': guessed_segment or '',
        'scrambled_segment': scrambled_segment or '',
        'is_sentence': is_sentence,
    }
    await state.update_data(scrambler=data)

    front_side = data_store.get('card_data', {}).get("front_side")
    if guessed_segment:
        text = generate_output_text(front=front_side, extra_text=guessed_segment)
    else:
        text = generate_output_text(front=front_side)
    await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN_V2,
                                     reply_markup=await kb.scramble_letters_output(
                                         dict(sorted(elements_count.items()))))


@router.callback_query(F.data.startswith('scramble_'))
@check_card_data
async def scramble_letters_check(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    user_answer = callback.data.split('_')[1]
    scrambler = data_store.get('scrambler', {})
    scrambled_segment = scrambler.get('scrambled_segment')
    guessed_segment = scrambler.get('guessed_segment', '')
    is_sentence = scrambler.get('is_sentence')

    current_element = scrambled_segment[0]
    if current_element == user_answer:
        guessed_segment += current_element if not is_sentence else f'{current_element} '
        scrambled_segment = scrambled_segment[1:]
        if len(scrambled_segment) != 0:
            await scramble_letters(callback, state=state, scrambled_segment=scrambled_segment,
                                   guessed_segment=guessed_segment, is_sentence=is_sentence)
        else:
            card_data = data_store.get('card_data')
            text = generate_output_text(card_data=card_data)
            await callback.message.delete()
            await state.update_data(scrambler={})
            await callback.message.answer(text, parse_mode=ParseMode.MARKDOWN_V2)

    else:
        await callback.answer('🤯🥳 Incorrect. Please try again.')
        await scramble_letters(callback, state=state, scrambled_segment=scrambled_segment,
                               guessed_segment=guessed_segment, is_sentence=is_sentence)


@router.callback_query(F.data.startswith('button_show_first_letters'))
@check_card_data
async def show_first_letters(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    card_data = data_store.get('card_data')
    front_side = card_data.get('front_side')
    prepared_text = card_data.get('back_side', '').split()
    max_len = max(map(len, prepared_text))

    step = callback.data.split('_')[-1]
    iteration = int(step) if step.isdigit() else 1

    if step and iteration * 2 >= max_len:
        text = generate_output_text(card_data=data_store.get('card_data', {}))
        await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN_V2)
        return

    masked_text = list(
        map(lambda x: x[:iteration * 2] + '*' * (len(x) - iteration * 2) if len(x) > iteration * 2 else x,
            prepared_text))

    text = generate_output_text(front=front_side, extra_text='  '.join(masked_text))
    button_name = f'show_first_letters_{iteration + 1}'
    buttons = {button_name: True}
    letters_to_show = (iteration + 1) * 2
    if max_len - iteration * 2 == 1:
        letters_to_show -= 1

    update_names = {
        button_name: f'Show {letters_to_show} letters'
    }

    await callback.message.edit_text(
        text,
        reply_markup=await kb.card_mode_buttons(buttons, update_names=update_names),
        parse_mode=ParseMode.MARKDOWN_V2)


@router.callback_query(F.data.in_(('button_speech', 'button_speech_locked')))
@check_card_data
async def text_to_speech(callback: CallbackQuery, state: FSMContext, data_store: dict = None):
    if callback.data == 'button_speech_locked':
        await callback.answer('The card has already been announced.')
        return
    card_data = data_store.get('card_data', {})
    start_config = data_store.get('start_config', {})

    buttons_to_show = start_config.get('buttons_to_show', {}).copy()
    buttons_to_show.pop('speech')
    buttons_to_show['speech_locked'] = True
    update_button_names = {'speech_locked': '🔊'}
    mappings_id = card_data.get('mappings_id')
    front_side = card_data.get("front_side")
    url_get_sound = start_config.get('urls', {}).get('get_sound', '')

    url = url_get_sound.replace('dummy_mappings_id', str(mappings_id))
    sound = await send_request(f"{BASE_URL}{url}")
    file = BufferedInputFile(sound, filename=front_side)

    text = generate_output_text(front=front_side)

    await callback.message.edit_text(
        text,
        reply_markup=await kb.card_mode_buttons(buttons_to_show, update_names=update_button_names),
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    await callback.message.answer_voice(file)


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию')
    await callback.message.answer('Выберите товар по категории',
                                  reply_markup=await kb.items(callback.data.split('_')[1]))


@router.callback_query(F.data.startswith('item_'))
async def category(callback: CallbackQuery):
    item_data = await rq.get_item(callback.data.split('_')[1])
    await callback.answer('Вы выбрали товар')
    await callback.message.answer(
        f'Название: {item_data.name}\nОписание: {item_data.description}\nЦена: {item_data.price}',
        reply_markup=await kb.items(callback.data.split('_')[1])
    )

# @router.message(CommandStart())
# async def cmd_start(message: Message):
#     await message.reply(f'Hi, your ID is {message.from_user.id} and name is {message.from_user.first_name}',
#                         reply_markup= kb.main)


# @router.message(Command('help'))
# async def get_help(message: Message):
#     await message.answer('Это команда "help"')
#
#
# @router.message(F.text == 'Как дела?')
# async def how_are_you(message: Message):
#     await message.answer('OK')
#
# @router.message(F.photo)
# async def photo(message: Message):
#     await message.answer(f'ID фото: {message.photo[-1].file_id}')
#
#
# @router.message(Command('get_photo'))
# async def get_photo(message: Message):
#     await message.answer_photo(photo='AgACAgIAAxkBAAMMZm8PUoRREpUZh4m27uM3NvaKK2kAAmD3MRsYDHhL_a5r0tZkZFEBAAMCAANtAAM1BA')
#
#
# @router.callback_query(F.data == 'catalog')
# async def catalog(callback: CallbackQuery):
#     await callback.answer('Вы выбрали каталог!')
#     await callback.message.edit_text('Привет!', reply_markup=await kb.inline_cars())
#
# #
# @router.message(Command('reg'))
# async def reg_one(message: Message, state: FSMContext):
#     await state.set_state(Reg.name)
#     await message.answer('Введите Ваше имя')
# #
# #
# @router.message(Reg.name)
# async def reg_two(message: Message, state: FSMContext):
#     await state.update_data(name=message.text)
#     await state.set_state(Reg.number)
#     await message.answer('Введите номер телефона')
#
#
# @router.message(Reg.number)
# async def two_three(message: Message, state: FSMContext):
#     await state.update_data(name=message.text)
#     data = await state.get_data()
#     await message.answer(f'Спасибо, регистрация завершена. \n {data}')
#     await state.clear()
#
# async def enter_mode(message: Message, state: FSMContext):
#     await state.set_state(CardMode.show_first_letters)
#     await message.reply("Режим 'показать первые буквы' активирован. Введите текст.")
