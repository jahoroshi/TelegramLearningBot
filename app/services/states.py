from aiogram.fsm.state import StatesGroup, State


class DeckRename(StatesGroup):
    new_name = State()


class DeckDelete(StatesGroup):
    active = State()


class DeckCreate(StatesGroup):
    name = State()


class ImportCards(StatesGroup):
    data = State()


class DeckViewingState(StatesGroup):
    active = State()


class CardManage(StatesGroup):
    card_ops_state = State()
    upd_list_index = State()
    del_list_index = State()
    front_side = State()
    back_side = State()
    is_two_sides = State()