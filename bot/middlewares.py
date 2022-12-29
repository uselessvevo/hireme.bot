from typing import Callable, Dict, Any, Union, Awaitable

from aiogram import types
from aiogram import BaseMiddleware
from bot.loader import db


ALLOWED_ROLES = ("is_admin", "is_employee")


class EmployeePermissionMiddleware(BaseMiddleware):

    def __init__(self, *args, role: ALLOWED_ROLES = "is_employee", **kwargs) -> None:
        if role not in ALLOWED_ROLES:
            raise KeyError("Key %s not found" % role)

        self._role = role
        super().__init__(*args, **kwargs)

    async def __call__(
        self,
        handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[types.Message, types.CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        user = await db.pool.fetchval(
            """
            SELECT 
                count(id) 
            FROM 
                users 
            WHERE 
                id = $1 
                AND %s = TRUE
            """ % self._role,
            int(event.from_user.id)
        )
        if not user:
            keyboard = [
                types.InlineKeyboardButton(
                    text="Отправить заявку",
                    callback_data="send_employee_register_request"
                )
            ]
            if isinstance(event, types.Message):
                await event.answer(
                    text="⚠️У вас нет доступа к этому разделу. Обратитесь к администрации.",
                    reply_markup=types.InlineKeyboardMarkup(
                        inline_keyboard=[keyboard]
                    )
                )
            else:
                await event.message.answer(
                    "⚠️У вас нет доступа к этому разделу. Обратитесь к администрации.",
                    reply_markup=types.InlineKeyboardMarkup(
                        inline_keyboard=[keyboard]
                    )
                )
        else:
            return await handler(event, data)
