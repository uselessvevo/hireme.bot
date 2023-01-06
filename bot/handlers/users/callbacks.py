from aiogram.filters.callback_data import CallbackData


class UserCallback(CallbackData, prefix="user_callback"):
    action: str
    user_id: int


class PaginationCallback(CallbackData, prefix="page_counter"):
    action: str  # next/previous
    offset: int
    user_id: int
