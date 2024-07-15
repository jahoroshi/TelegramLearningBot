import functools


def check_current_state(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        state = kwargs.get('state')
        current_state = await state.get_state()
        if current_state in ('DeckViewingState:active', 'CardManage:card_ops_state', 'CardManage:is_two_sides'):
            return await func(*args, **kwargs)
        else:
            print(current_state)
            print(kwargs)
            from app.handlers import to_decks_list
            return await to_decks_list(*args, **kwargs)

    return wrapper
