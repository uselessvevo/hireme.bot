from aiogram import types
from aiogram import Router
from aiogram import filters
from aiogram.fsm.context import FSMContext

from bot.loader import db
from bot.handlers.users.callbacks import UserCallback
from bot.middlewares import EmployeePermissionMiddleware


router = Router(name="search.main")
router.message.middleware(EmployeePermissionMiddleware())
router.callback_query.middleware(EmployeePermissionMiddleware())


@router.callback_query(filters.Text("search_request"))
async def users_list(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()

    users = await db.pool.fetch(
        """
        SELECT
            u.id,
            u.email,
            u.resume_url,
            u.firstname,
            u.middlename,
            u.patronymic,
            f.id as filter_id
        FROM 
            users u
        LEFT JOIN 
            filters f 
        ON 
            u.id = f.user_id
        WHERE
            curator_id = $1
        ORDER BY 
            u.id
        LIMIT 1
        """,
        callback.from_user.id
    )

    if not users:
        await callback.message.answer(
            text="Список пользователей пуст. Создать?",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="Регистрация",
                            callback_data="register_user"
                        )
                    ]
                ]
            )
        )
        return

    for user in users:
        user = dict(user)
        button = [
            types.InlineKeyboardButton(
                text="Выбрать существующий фильтр",
                callback_data=UserCallback(
                    action="pick_existed_filter",
                    user_id=user.get("id")
                ).pack()
            )
        ] if user.get("filter_id") else [
                types.InlineKeyboardButton(
                    text="Выбрать",
                    callback_data=UserCallback(
                        action="register_filter",
                        user_id=user.get("id")
                    ).pack()
                )
            ]

        fullname = " ".join(user.get(i) for i in ("middlename", "firstname", "patronymic"))
        await callback.message.answer(
            f"📌 *ФИО:* _{fullname}_\n\n"
            f"📌 *Эл. Почта:* _{user.get('email')}_\n\n"
            f"📌 Ссылка на резюме: {user.get('resume_url')}",
            parse_mode="Markdown",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[button]
            )
        )
