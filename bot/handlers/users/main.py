from aiogram import types
from aiogram import Router
from aiogram import filters
from aiogram.fsm.context import FSMContext

from bot.loader import db
from bot.handlers.users.callbacks import UserCallback, PaginationCallback
from bot.middlewares import EmployeePermissionMiddleware


router = Router(name="users.main")
router.message.middleware(EmployeePermissionMiddleware())
router.callback_query.middleware(EmployeePermissionMiddleware())


@router.callback_query(filters.Text("users_list"))
async def users_list(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()

    users = await db.pool.fetch(
        """
        SELECT DISTINCT on(u.id)
            u.id,
            u.email,
            u.resume_url,
            u.firstname,
            u.middlename,
            u.patronymic,
            l.content as letter
        FROM 
            users u
        LEFT JOIN 
            letters l 
        ON 
            u.id = l.user_id
        WHERE
            is_employee = FALSE
        """
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
        fullname = " ".join(user.get(i) for i in ("middlename", "firstname", "patronymic"))
        await callback.message.answer(
            f"📌 *ФИО:* _{fullname}_\n\n"
            f"📌 *Эл. Почта:* _{user.get('email')}_\n\n"
            f"📌 Ссылка на резюме: https://hh.ru/resume/{user.get('resume_url')}\n\n"
            f"📌 Сопроводительное письмо: \n\n{user.get('letter')}",
            parse_mode="Markdown",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="Редактировать",
                            callback_data=UserCallback(
                                action="edit_user",
                                user_id=user.get("id")
                            ).pack()
                        ),
                        types.InlineKeyboardButton(
                            text="Показать отклики",
                            callback_data=PaginationCallback(
                                action="show_vacancies",
                                offset=0,
                                user_id=user.get("id")
                            ).pack()
                        )
                    ]
                ]
            )
        )
