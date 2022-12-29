from aiogram import F
from aiogram import types
from aiogram import Router
from aiogram import filters
from aiogram.fsm.context import FSMContext

from bot.handlers.users.callbacks import UserCallback
from bot.loader import db
from bot.handlers.admin.callbacks import EmployeeRegisterCallback

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


@router.callback_query(filters.Text("show_employee_requests"))
async def show_employee_requests(callback: types.CallbackQuery) -> None:
    requests = await db.pool.fetch(
        """
        SELECT * FROM employee_requests
        """
    )
    for request in requests:
        request = dict(request)
        await callback.message.answer(
            text=f"Имя пользователя: {request.get('username')}\n"
                 f"Id пользователя: {request.get('user_id')}",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="Подтвердить",
                            callback_data=EmployeeRegisterCallback(
                                user_id=request.get("user_id"),
                                username=request.get("username")
                            ).pack()
                        )
                    ]
                ]
            )
        )


@router.callback_query(EmployeeRegisterCallback.filter())
async def accept_new_employee(callback: types.CallbackQuery, callback_data: EmployeeRegisterCallback) -> None:
    from bot.loader import bot
    await db.pool.execute(
        """
        INSERT INTO
            users (id, curator_id, firstname, middlename, patronymic, resume_url, email, password, is_employee, is_admin) 
        VALUES
            ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """,
        callback_data.user_id,
        None,
        callback_data.username,
        "-",
        "-",
        "-",
        "-",
        "-",
        True,
        False
    )
    await bot.send_message(callback_data.user_id, "Вы были зарегистрированы")
    await callback.message.answer("Пользователь %s был добавлен" % callback_data.username)
