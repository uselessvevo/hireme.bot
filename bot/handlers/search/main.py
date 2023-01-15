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
async def search_request(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()

    users = await db.pool.fetch(
        """
        SELECT distinct on(u.id)
            u.id,
            u.email,
            u.resume_url,
            u.firstname,
            u.middlename,
            u.patronymic,
            f.id as filter_id,
            l.content as letter
        FROM 
            users u
        LEFT JOIN 
            letters l 
        ON 
            u.id = l.user_id
        LEFT JOIN 
            filters f
        ON 
            u.id = f.user_id
        WHERE
            u.is_employee = FALSE
        ORDER BY 
            u.id
        """,
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
        buttons = [
            types.InlineKeyboardButton(
                text="✏️ Создать",
                callback_data=UserCallback(
                    action="register_filter",
                    user_id=user.get("id")
                ).pack()
            )
        ]
        if user.get("filter_id"):
            buttons.insert(
                0,
                types.InlineKeyboardButton(
                    text="🚀 Выбрать",
                    callback_data=UserCallback(
                        action="pick_existed_filter",
                        user_id=user.get("id")
                    ).pack()
                )
            )

        fullname = " ".join(user.get(i) for i in ("middlename", "firstname", "patronymic"))
        await callback.message.answer(
            f"📌 *ФИО:* _{fullname}_\n\n"
            f"📌 *Эл. Почта:* _{user.get('email')}_\n\n"
            f"📌 Ссылка на резюме: https://hh.ru/resume/{user.get('resume_url')}\n\n"
            f"📌 Сопроводительное письмо: \n\n{user.get('letter')}",
            parse_mode="Markdown",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[buttons]
            )
        )
