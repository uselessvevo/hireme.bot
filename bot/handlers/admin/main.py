from aiogram import types
from aiogram import Router
from aiogram import filters
from aiogram.fsm.context import FSMContext

from bot.loader import db
from bot.middlewares import EmployeePermissionMiddleware
from bot.handlers.admin.callbacks import EmployeeRegisterCallback


router = Router(name="admin.main")
router.message.middleware(EmployeePermissionMiddleware(role="is_admin"))
router.callback_query.middleware(EmployeePermissionMiddleware(role="is_admin"))


@router.callback_query(filters.Text("admin_menu"))
async def admin_menu(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(
        text="Выберите пункт меню",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Показать заявки новых пользователей",
                        callback_data="show_employee_requests"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="Показать активные задачи",
                        callback_data="show_active_tasks"
                    )
                ],
            ]
        )
    )


@router.callback_query(filters.Text("show_active_tasks"))
async def show_active_tasks(callback: types.CallbackQuery, state: FSMContext) -> None:
    pass


@router.callback_query(filters.Text("show_employee_requests"))
async def show_employee_requests(callback: types.CallbackQuery) -> None:
    requests = await db.pool.fetch(
        """
        SELECT * FROM employee_requests
        """
    )
    if not requests:
        await callback.message.answer("Нет активных заявок")

    for request in requests:
        request = dict(request)
        await callback.message.answer(
            f"Имя пользователя: {request.get('username')}\n"
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
