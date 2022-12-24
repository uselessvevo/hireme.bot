import typing
from aiogram import types
from aiogram import BaseMiddleware

from bot.loader import db


class EmployeePermissionMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: typing.Callable[[types.Message, typing.Dict[str, typing.Any]], typing.Awaitable[typing.Any]],
        event: typing.Union[types.Message, types.CallbackQuery],
        data: typing.Dict[str, typing.Any]
    ) -> typing.Any:
        user = await db.pool.fetch(
            """
            SELECT * FROM users WHERE id = $1 AND is_employee = TRUE
            """,
            int(event.from_user.id)
        )
        if not user:
            if isinstance(event, types.Message):
                await event.answer("⚠️У вас нет доступа к этому боту. Обратитесь к администрации.")
            else:
                await event.message.answer("⚠️У вас нет доступа к этому боту. Обратитесь к администрации.")
        else:
            return await handler(event, data)
