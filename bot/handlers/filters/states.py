from aiogram.fsm.state import StatesGroup, State


class FilterCreateState(StatesGroup):
    areas = State()
    salary = State()
    user = State()
    is_ready = State()
    finish = State()
