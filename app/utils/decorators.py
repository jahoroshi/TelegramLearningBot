import functools

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from app.states import DeckViewingState

# from app.middlewares import TestMiddleware

router = Router()


def check_current_state(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        state = kwargs.get('state')
        current_state = await state.get_state()
        func_name = func.__name__
        permissions = {
            'card_update_create_handler': (
                'CardManage:is_two_sides',
                'CardManage:addcard_slug'
            ),
            'global': (
                'DeckViewingState:active',
                'CardManage:card_ops_state'
            )
        }
        if permissions.get(func_name):
            if current_state in permissions[func_name]:
                return await func(*args, **kwargs)
            else:
                from app.services import handle_to_decks_list
                return await handle_to_decks_list(*args, **kwargs)

        if current_state in permissions['global']:
            return await func(*args, **kwargs)

        from app.services import handle_to_decks_list
        return await handle_to_decks_list(*args, **kwargs)

    return wrapper


def clear_current_state(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        state = kwargs.get('state')
        current_state = await state.get_state()
        if current_state not in ('DeckViewingState:active', 'CardManage:card_ops_state', 'CardManage:is_two_sides'):
            await state.clear()
            await state.set_state(DeckViewingState.active)
        return await func(*args, **kwargs)

    return wrapper


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
        state: FSMContext = kwargs.get('state')
        data_store = await state.get_data()
        card_data = data_store.get('card_data')
        kwargs['data_store'] = data_store
        if card_data is None:
            from app.services.cardmode.cardmode_start import process_card_mode_start
            await process_card_mode_start(message=msg, state=state)
            return
        return await func(*args, **kwargs)

    return wrapper
