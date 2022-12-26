from aiogram.fsm.state import StatesGroup, State


class FilterCreateState(StatesGroup):
    text = State()
    letter = State()
    areas = State()
    salary = State()
    user = State()
    is_ready = State()
    finish = State()
