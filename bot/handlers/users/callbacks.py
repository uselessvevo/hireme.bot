from aiogram.filters.callback_data import CallbackData


class UserCallback(CallbackData, prefix="user_callback"):
    action: str
    user_id: int


class PaginationCallback(CallbackData, prefix="pagination"):
    action: str  # next/previous/manually
    offset: int
    user_id: int
    status: str = "all"


class CreateUserCallback(CallbackData, prefix="user_create"):
    state: str
