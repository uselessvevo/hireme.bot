import asyncpg
from typing import Union, Any

from aiogram import F
from aiogram import types
from aiogram import Router
from aiogram.fsm.context import FSMContext

from bot.loader import db
from bot.handlers.users.callbacks import PaginationCallback
from bot.middlewares import EmployeePermissionMiddleware


router = Router(name="users.callbacks_router")
router.message.middleware(EmployeePermissionMiddleware())
router.callback_query.middleware(EmployeePermissionMiddleware())


async def pagination_keyboard_factory(
    callback_data: PaginationCallback,
    state: FSMContext
) -> list[Union[list, list[types.InlineKeyboardButton, Any]]]:
    #                                        v --- pressed
    # Pagination must be like this: [1 2 3 4 5 ... max] -> [3 4 5 6 7 ... max]
    state_data = await state.get_data()
    page_amount = state_data.get("page_amount")
    current_offset = int(state_data.get("current_offset", 0))

    page_buttons: list[types.InlineKeyboardButton] = []
    arrow_buttons: list[types.InlineKeyboardButton] = [
        types.InlineKeyboardButton(
            text="←",
            callback_data=PaginationCallback(
                action="previous",
                offset=10,
                user_id=callback_data.user_id
            ).pack()
        ),
        types.InlineKeyboardButton(
            text="→",
            callback_data=PaginationCallback(
                action="next",
                offset=10,
                user_id=callback_data.user_id
            ).pack()
        )
    ]

    stop_page_slice = 5
    if (current_offset // 10) + 1 == page_amount:
        stop_page_slice = page_amount
    elif current_offset > 10:
        stop_page_slice = current_offset // 10 + 3

    for page in range(
        0 if current_offset <= 10 else current_offset // 10 - 2,
        stop_page_slice
    ):
        page_buttons.append(
            types.InlineKeyboardButton(
                text=str(page + 1),
                callback_data=PaginationCallback(
                    action="manually",
                    offset=page * 10,
                    user_id=callback_data.user_id,
                ).pack()
            )
        )

    page_buttons.append(
        types.InlineKeyboardButton(
            text=str(page_amount),
            callback_data=PaginationCallback(
                action="manually",
                offset=page_amount * 10,
                user_id=callback_data.user_id,
            ).pack()
        )
    )
    page_buttons.insert(
        -1,
        types.InlineKeyboardButton(
            text="...",
            callback_data="__UNHANDLED__"
        )
    )

    return [page_buttons, arrow_buttons]


@router.callback_query(PaginationCallback.filter(F.action == "show_vacancies"))
async def show_vacancies(
    callback: types.CallbackQuery,
    callback_data: PaginationCallback,
    state: FSMContext
) -> None:
    # Get all vacancies callbacks for our user and count them
    vacancies = await db.pool.fetch(
        """
        SELECT * FROM vacancies WHERE user_id = $1
        """,
        callback_data.user_id
    )
    page_amount = round(len(vacancies) / 100 * 10)
    await state.update_data({"page_amount": page_amount})

    if not vacancies:
        await callback.message.answer("Откликов не найдено")

    elif len(vacancies) <= 10:
        await show_vacancies(callback.message, callback_data, state, 0)

    else:
        state_data = await state.get_data()
        await show_vacancies(callback.message, callback_data, state, state_data.get("current_offset", 0))


@router.callback_query(PaginationCallback.filter())
async def change_offset(
    callback: types.CallbackQuery,
    callback_data: PaginationCallback,
    state: FSMContext
) -> None:
    if callback_data.action in ("next", "previous", "manually"):
        state_data = await state.get_data()
        current_offset = state_data.get("current_offset", 0)
        if callback_data.action == "next":
            current_offset = callback_data.offset  # + 10
        elif callback_data.action == "previous":
            current_offset = callback_data.offset - 10
        elif callback_data.action == "manually":
            current_offset = callback_data.offset

        if current_offset < 0:
            current_offset = 0
        if current_offset == state_data.get("page_amount") * 10:
            current_offset = state_data.get("page_amount") * 10 - 10

        await state.update_data({"current_offset": current_offset})
        await show_vacancies(callback.message, callback_data, state, current_offset)


async def show_vacancies(
    message: types.Message,
    callback_data: PaginationCallback,
    state: FSMContext,
    offset: int
) -> None:
    vacancies = await db.pool.fetch(
        """
        SELECT * FROM vacancies WHERE user_id = $1 LIMIT 10 OFFSET $2
        """,
        callback_data.user_id,
        offset
    )
    buttons = await pagination_keyboard_factory(callback_data, state)

    for vacancy in vacancies:
        vacancy = dict(vacancy)
        await message.answer(
            f"{vacancy.get('id')}\n"
            f"**{vacancy.get('title')}**\n\n"
            f"Зарплата: *{vacancy.get('salary')}*\n"
            f"Ссылка: {vacancy.get('url')}",
            parse_mode="Markdown"
        )

    await message.answer(
        text="Выберите страницу или нажмите 'Далее/Назад'",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=buttons
        )
    )
