from aiogram import F
from aiogram import types
from aiogram import Router
from aiogram import filters
from aiogram.fsm.context import FSMContext
from telegram_bot_pagination import InlineKeyboardPaginator

from bot.loader import db
from bot.handlers.users.callbacks import UserCallback
from bot.middlewares import EmployeePermissionMiddleware


router = Router(name="users.callbacks_router")
router.message.middleware(EmployeePermissionMiddleware())
router.callback_query.middleware(EmployeePermissionMiddleware())


async def send_character_page(message: types.Message, vacancies: list[str], page: int = 1):
    paginator = InlineKeyboardPaginator(
        len(vacancies),
        current_page=page,
        data_pattern='character#{page}'
    )

    await message.answer(
        vacancies[page-1],
        reply_markup=paginator.markup,
        parse_mode='Markdown'
    )


@router.callback_query(UserCallback.filter(F.action == "show_vacancies_callback"))
async def show_vacancies_callback(callback: types.CallbackQuery, callback_data: UserCallback, state: FSMContext) -> None:
    vacancies = await db.pool.fetch(
        """
        SELECT * FROM vacancies WHERE user_id = $1
        """,
        callback_data.user_id
    )
    # show every 10 elements; add next/previous button;
    # save page in FSM state
    for vacancy in vacancies:
        vacancy = dict(vacancy)
        await callback.message.answer(
            f"**{vacancy.get('title')}**\n\n"
            f"Зарплата: *{vacancy.get('salary')}*\n"
            f"Ссылка: {vacancy.get('url')}"
        )
