from aiogram.fsm.state import StatesGroup, State


class RegisterUserStates(StatesGroup):
    email = State()
    password = State()
    resume_url = State()
    middlename = State()
    firstname = State()
    patronymic = State()
    transmittal_letter = State()
    finish = State()


class EditUserStates(StatesGroup):
    start = State()
    email = State()
    resume_url = State()
    firstname = State()
    middlename = State()
    patronymic = State()
    curator_id = State()
    password = State()
    letter = State()


class ApplyFilterStates(StatesGroup):
    start = State()
    area = State()
    vacancies_amount = State()
    periodicity_days = State()

