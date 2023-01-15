from aiogram import F
from aiogram import types
from aiogram import Router
from aiogram import filters
from aiogram.fsm.context import FSMContext

from bot.loader import db
from bot.handlers.users.callbacks import UserCallback
from bot.middlewares import EmployeePermissionMiddleware
from bot.handlers.filters.states import FilterCreateState
from bot.handlers.filters.helpers import build_area_filter
from bot.handlers.filters.helpers import build_filter_json
from bot.handlers.filters.helpers import build_result_filter
from bot.handlers.filters.helpers import build_salary_filter
from bot.handlers.filters.helpers import build_text_filter

from bot.requests import request_start_task

router = Router(name="fitlers.create")
router.message.middleware(EmployeePermissionMiddleware())
router.callback_query.middleware(EmployeePermissionMiddleware())


@router.callback_query(UserCallback.filter(F.action == "register_filter"))
async def register_filter(callback: types.CallbackQuery, callback_data: UserCallback, state: FSMContext) -> None:
    await state.clear()
    await callback.message.delete()

    await callback.message.answer(
        "Для создания фильтра: \n"
        "📌 Страны, регионы или области\n"
        "📌 Заработная плата (опционально)\n\n"
        "Начнём?",
        disable_web_page_preview=True,
        parse_mode="markdown",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Да",
                        callback_data=UserCallback(
                            action="register_filter_start",
                            user_id=callback_data.user_id,
                        ).pack()
                    ),
                    types.InlineKeyboardButton(
                        text="Нет",
                        callback_data="filters_list"
                    )
                ]
            ]
        )
    )


@router.callback_query(UserCallback.filter(F.action == "register_filter_start"))
async def text_request_prompt(callback: types.CallbackQuery, callback_data: UserCallback, state: FSMContext) -> None:
    await callback.message.delete()
    await callback.message.answer("Введите текст запроса. К примеру: Python junior'")
    await state.update_data({"user_id": callback_data.user_id})
    await state.set_state(FilterCreateState.letter)


@router.message(filters.StateFilter(FilterCreateState.letter))
async def letter_prompt(message: types.Message, state: FSMContext) -> None:
    if not message.text.strip():
        await message.answer("Введите корректный текст запроса. К примеру, Python junior")
        return

    await state.update_data({"text": message.text.strip()})
    await state.update_data({"text_url": await build_text_filter(message.text.strip())})
    await message.answer("Отлично! Теперь введите сопроводительное письмо.")
    await state.set_state(FilterCreateState.areas)


@router.message(filters.StateFilter(FilterCreateState.areas))
async def areas_prompt(message: types.Message, state: FSMContext) -> None:
    if not message.text.strip():
        await message.answer("Введите текст сопроводительного письма")
        return

    await state.update_data({"letter": message.text})
    await message.answer("Отлично! Теперь введите название стран через запятую")
    await state.set_state(FilterCreateState.salary)


@router.message(filters.StateFilter(FilterCreateState.salary))
async def salary_prompt(message: types.Message, state: FSMContext) -> None:
    areas_url = await build_area_filter(message.text)
    if not areas_url:
        await message.answer("Введите корректное наименование стран, регионов или областей (через запятую)")
        return

    await state.update_data({"areas_url": areas_url})
    await state.update_data({"areas": [i.strip() for i in message.text.strip().split(",")]})
    await message.answer(
        "Отлично! Теперь введите желаемый уровень дохода\n\n*ВВЕДИТЕ \"-\" ДЛЯ ПРОПУСКА*",
        parse_mode="Markdown"
    )
    await state.set_state(FilterCreateState.is_ready)


@router.message(filters.StateFilter(FilterCreateState.is_ready))
async def filter_register_finish(message: types.Message, state: FSMContext) -> None:
    salary_url = await build_salary_filter(message.text)
    if message.text == "-":
        salary_url = None

    elif not salary_url:
        await message.answer(
            "Введите корректный уровень дохода\n\n*ВВЕДИТЕ \"-\" ДЛЯ ПРОПУСКА*",
            parse_mode="Markdown"
        )
        return

    await state.update_data({"salary_url": salary_url})
    await state.update_data({"salary": int(message.text)})

    await message.answer(
        "Всё готово. Сохранить?",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Да",
                        callback_data="filter_register_finish"
                    ),
                    types.InlineKeyboardButton(
                        text="Нет, начать заново",
                        callback_data="register_filter"
                    )
                ]
            ]
        )
    )
    await state.set_state(FilterCreateState.finish)


@router.callback_query(filters.Text("filter_register_finish"))
@router.callback_query(filters.StateFilter(FilterCreateState.finish))
async def filter_register_finish(callback: types.CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()
    # state_data.update({"filter_url": await build_resume_url_filter(state_data.get("user_id"))})

    filter_data = {k: v for (k, v) in state_data.items() if k in ("areas", "salary", "text", "letter")}
    filter_data = await build_filter_json(filter_data)

    filter_string = await build_result_filter([state_data.get(i) for i in (
        "areas_url", "salary_url", "text_url",
    )])

    await db.pool.execute(
        """
        INSERT INTO
            filters (filter, filter_url, user_id)
        VALUES
            ($1, $2, $3)
        """,
        filter_data,
        filter_string,
        int(state_data.get("user_id")),
    )
    await request_start_task(callback.from_user.id, state_data.get("user_id"))

    await callback.message.answer("Всё готово!")
    await state.clear()


@router.callback_query(UserCallback.filter(F.action == "pick_existed_filter"))
async def pick_existed_filter(callback: types.CallbackQuery, callback_data: UserCallback) -> None:
    filter_data = await db.pool.fetchrow(
        """
        SELECT 
            * 
        FROM 
            filters 
        WHERE 
            user_id = $1 
        ORDER BY 
            id 
        LIMIT 1
        """,
        int(callback_data.user_id)
    )
    await request_start_task(callback.from_user.id, filter_data.get("user_id"))
    await callback.message.answer("Начинаем рассылку!")
