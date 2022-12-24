from aiogram.filters.callback_data import CallbackData


class UserCallback(CallbackData, prefix="user_callback"):
    action: str
    user_id: int
