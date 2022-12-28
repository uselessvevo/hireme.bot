from aiogram.filters.callback_data import CallbackData


class EmployeeRegisterCallback(CallbackData, prefix="empreg_cb"):
    user_id: int
    username: str
