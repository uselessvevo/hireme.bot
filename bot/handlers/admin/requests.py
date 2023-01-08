from aiogram import types
from aiogram import Router
from aiogram import filters

from bot.loader import db

router = Router(name="admin.requests")


@router.callback_query(filters.Text("send_employee_register_request"))
async def send_employee_register_request(callback: types.CallbackQuery) -> None:
    await db.pool.execute(
        """
        INSERT INTO employee_requests (user_id, username) VALUES ($1, $2)
        """,
        callback.from_user.id,
        callback.from_user.username
    )
    await callback.message.answer("Заявка зарегистрирована. Ожидайте.")
