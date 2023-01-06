from aiogram import types
from aiogram import Router
from aiogram import filters
from aiogram.fsm.context import FSMContext

from bot.middlewares import EmployeePermissionMiddleware

router = Router(name="root.start")
router.message.middleware(EmployeePermissionMiddleware())
router.callback_query.middleware(EmployeePermissionMiddleware())


@router.message(filters.Command(commands=["start"]))
async def start(message: types.Message, state: FSMContext) -> None:
    await message.delete()
    await state.clear()
    await message.answer(
        text="Выбор действия",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Регистрация ✨",
                        callback_data="register_user"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="Пользователи 📋",
                        callback_data="users_list"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="Поисковой запрос",
                        callback_data="search_request"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="Админ. панель",
                        callback_data="admin_menu"
                    )
                ]
            ]
        )
    )
