from aiogram import types
from aiogram import Router
from aiogram import filters
from aiogram.fsm.context import FSMContext

from bot.handlers.users.callbacks import UserCallback
from bot.middlewares import EmployeePermissionMiddleware


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
