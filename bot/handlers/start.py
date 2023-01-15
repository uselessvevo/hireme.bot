from aiogram import types
from aiogram import Router
from aiogram import filters
from aiogram.fsm.context import FSMContext

from bot.loader import db
from bot.middlewares import EmployeePermissionMiddleware

router = Router(name="root.start")
router.message.middleware(EmployeePermissionMiddleware())
router.callback_query.middleware(EmployeePermissionMiddleware())


@router.message(filters.Command(commands=["start"]))
async def start(message: types.Message, state: FSMContext) -> None:
    await message.delete()
    await state.clear()

    keyboard = [
        [
            types.InlineKeyboardButton(
                text="✨ Регистрация",
                callback_data="register_user"
            )
        ],
        [
            types.InlineKeyboardButton(
                text="📋 Пользователи",
                callback_data="users_list"
            )
        ],
        [
            types.InlineKeyboardButton(
                text="🤖 Рассылка",
                callback_data="search_request"
            )
        ]
    ]

    if await db.pool.fetchval(
        """
        SELECT is_admin FROM users WHERE id = $1
        """,
        message.from_user.id
    ):
        keyboard.insert(
            0,
            [
                types.InlineKeyboardButton(
                    text="⚔️ Админ. панель",
                    callback_data="admin_menu"
                )
            ]
        )

    await message.answer(
        text="Выбор действия",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=keyboard
        )
    )
