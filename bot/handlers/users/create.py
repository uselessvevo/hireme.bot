from aiogram import types
from aiogram import Router
from aiogram import filters
from aiogram.fsm.context import FSMContext

from bot.loader import db
from bot.middlewares import EmployeePermissionMiddleware
from bot.handlers.users.states import RegisterUserStates
from bot.handlers.helpers import check_name, check_url, check_email, check_password

router = Router(name="users.create")
router.message.middleware(EmployeePermissionMiddleware())
router.callback_query.middleware(EmployeePermissionMiddleware())


@router.callback_query(filters.Text("register_user"))
async def register_user(callback: types.CallbackQuery) -> None:
    await callback.message.answer(
        "Для создания пользователя понадобится поэтапно ввести следующие данные: \n"
        "📌 Ссылка на [резюме на hh.ru](https://hh.ru)\n"
        "📌 Эл. почта"
        "📌 Фамилию, имя и отчество\n"
        "📌 Сопроводительное письмо\n\n"
        "Начнём?",
        disable_web_page_preview=True,
        parse_mode="markdown",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Да",
                        callback_data="register_user_start"
                    ),
                    types.InlineKeyboardButton(
                        text="Нет",
                        callback_data="users_list"
                    )
                ]
            ]
        )
    )


@router.callback_query(filters.Text("register_user_start"))
async def username_prompt(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer("Введите эл. почту")
    await state.set_state(RegisterUserStates.email)


@router.message(filters.StateFilter(RegisterUserStates.email))
async def resume_prompt(message: types.Message, state: FSMContext) -> None:
    username = await check_email(message.text)
    if not username:
        await message.answer("Введите корректную эл. почту")
        return

    await state.update_data({"email": message.text})
    await message.answer("Отлично! Теперь введите ссылку на резюме (hh.ru)")
    await state.set_state(RegisterUserStates.resume_url)


@router.message(filters.StateFilter(RegisterUserStates.resume_url))
async def password_prompt(message: types.Message, state: FSMContext) -> None:
    resume_url = await check_url(message.text)
    if not resume_url:
        await message.answer("Введите корректную ссылку на резюме (https://...)")
        return

    await state.update_data({"resume_url": resume_url})
    await message.answer("Отлично! Теперь введите пароль")
    await state.set_state(RegisterUserStates.password)


@router.message(filters.StateFilter(RegisterUserStates.password))
async def middlename_prompt(message: types.Message, state: FSMContext) -> None:
    password = await check_password(message.text)
    if not password:
        await message.answer("Введите корректный пароль (латинские буквы + цифры)")

    await message.delete()
    await state.update_data({"password": message.text})
    await message.answer(
        "Отлично! Теперь введите *фамилию*",
        parse_mode="Markdown"
    )
    await state.set_state(RegisterUserStates.middlename)


@router.message(filters.StateFilter(RegisterUserStates.middlename))
async def firstname_prompt(message: types.Message, state: FSMContext) -> None:
    if not await check_name(message.text):
        await message.answer("Некорректная фамилия")
        return

    await state.update_data({"middlename": message.text})
    await message.answer("Введите имя")
    await state.set_state(RegisterUserStates.firstname)


@router.message(filters.StateFilter(RegisterUserStates.firstname))
async def patronymic_prompt(message: types.Message, state: FSMContext) -> None:
    if not await check_name(message.text):
        await message.answer("Некорректное имя")
        return

    await state.update_data({"firstname": message.text})
    await message.answer("Введите отчество")
    await state.set_state(RegisterUserStates.patronymic)


@router.message(filters.StateFilter(RegisterUserStates.patronymic))
async def transmittal_letter_prompt(message: types.Message, state: FSMContext) -> None:
    if not await check_name(message.text):
        await message.answer("Некорректное отчество")
        return

    await state.update_data({"patronymic": message.text})
    await message.answer("Введите сопроводительное письмо")
    await state.set_state(RegisterUserStates.transmittal_letter)


@router.message(filters.StateFilter(RegisterUserStates.transmittal_letter))
async def user_register_finish(message: types.Message, state: FSMContext) -> None:
    await state.update_data({"transmittal_letter": message.text})
    await message.answer(
        "Всё готово. Сохранить?",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Да",
                        callback_data="user_register_finish"
                    ),
                    types.InlineKeyboardButton(
                        text="Нет, начать заново",
                        callback_data="register_user"
                    )
                ]
            ]
        )
    )
    await state.set_state(RegisterUserStates.finish)


@router.callback_query(filters.Text("user_register_finish"))
@router.callback_query(filters.StateFilter(RegisterUserStates.finish))
async def user_register_finish(callback: types.CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()
    await db.pool.execute(
        """
        insert into
            users (
                id,
                curator_id,
                email,
                resume_url,
                password,
                firstname, 
                middlename, 
                patronymic
            )
        values
            (default, $1, $2, $3, $4, $5, $6, $7)
        """,
        callback.from_user.id,
        state_data.get("email"),
        state_data.get("resume_url"),
        state_data.get("password"),
        state_data.get("firstname"),
        state_data.get("middlename"),
        state_data.get("patronymic"),
    )
    await db.pool.execute(
        """
        insert into 
            letters (content, user_id) 
        values 
            ($1, $2)
        """,
        state_data.get("transmittal_letter"),
        callback.from_user.id
    )
    await callback.message.answer("Всё готово!")
    await state.clear()