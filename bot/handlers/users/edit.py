from aiogram import F
from aiogram import types
from aiogram import Router
from aiogram import filters
from aiogram.fsm.context import FSMContext

from bot.loader import db
from bot.handlers.users.states import EditUserStates
from bot.handlers.users.callbacks import UserCallback
from bot.middlewares import EmployeePermissionMiddleware
from bot.handlers.helpers import check_email, check_password, check_name, check_url

router = Router(name="users.edit")
router.message.middleware(EmployeePermissionMiddleware())
router.callback_query.middleware(EmployeePermissionMiddleware())


@router.message(EditUserStates.start)
@router.callback_query(UserCallback.filter(F.action == "edit_user"))
async def edit_menu(callback: types.CallbackQuery, callback_data: UserCallback, state: FSMContext) -> None:
    await state.clear()
    await callback.message.delete()

    await callback.message.answer(
        text="Выберите поле для редактирования",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Фамилия",
                        callback_data=UserCallback(action="middlename", user_id=callback_data.user_id).pack()
                    ),
                    types.InlineKeyboardButton(
                        text="Имя",
                        callback_data=UserCallback(action="firstname", user_id=callback_data.user_id).pack()
                    ),
                    types.InlineKeyboardButton(
                        text="Отчество",
                        callback_data=UserCallback(action="patronymic", user_id=callback_data.user_id).pack()
                    ),
                ],
                [
                    types.InlineKeyboardButton(
                        text="Эл. Почта",
                        callback_data=UserCallback(action="email", user_id=callback_data.user_id).pack()
                    ),
                    types.InlineKeyboardButton(
                        text="Пароль",
                        callback_data=UserCallback(action="password", user_id=callback_data.user_id).pack()
                    ),
                ],
                [
                    types.InlineKeyboardButton(
                        text="Ссылка на резюме",
                        callback_data=UserCallback(action="resume_url", user_id=callback_data.user_id).pack()
                    ),
                    types.InlineKeyboardButton(
                        text="Сопроводительно письмо",
                        callback_data=UserCallback(action="letter", user_id=callback_data.user_id).pack()
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="Назад",
                        callback_data="users_list"
                    ),
                ]
            ]
        )
    )


@router.callback_query(UserCallback.filter(F.action == "middlename"))
async def prompt_middlename(callback: types.CallbackQuery, callback_data: UserCallback, state: FSMContext) -> None:
    await state.update_data({"user_id": callback_data.user_id})
    await callback.message.answer("Введите фамилию")
    await state.set_state(EditUserStates.middlename)


@router.message(filters.StateFilter(EditUserStates.middlename))
async def confirm_middlename(message: types.Message, state: FSMContext) -> None:
    if not await check_name(message.text):
        await message.answer("Введите корректную фамилию")
        return

    state_data = await state.get_data()
    await db.pool.execute(
        """
        UPDATE users SET "middlename" = $2 WHERE id = $1
        """,
        int(state_data.get("user_id")),
        message.text
    )
    await message.answer("Фамилия обновлена")
    await state.set_state(EditUserStates.start)


@router.callback_query(UserCallback.filter(F.action == "firstname"))
async def prompt_firstname(callback: types.CallbackQuery, callback_data: UserCallback, state: FSMContext) -> None:
    await state.update_data({"user_id": callback_data.user_id})
    await callback.message.answer("Введите имя")
    await state.set_state(EditUserStates.firstname)


@router.message(filters.StateFilter(EditUserStates.firstname))
async def confirm_firstname(message: types.Message, state: FSMContext) -> None:
    if not await check_name(message.text):
        await message.answer("Введите корректное имя")
        return

    state_data = await state.get_data()
    await db.pool.execute(
        """
        UPDATE users SET "firstname" = $2 WHERE id = $1
        """,
        int(state_data.get("user_id")),
        message.text
    )
    await message.answer("Имя обновлено")
    await state.set_state(EditUserStates.start)


@router.callback_query(UserCallback.filter(F.action == "patronymic"))
async def prompt_patronymic(callback: types.CallbackQuery, callback_data: UserCallback, state: FSMContext) -> None:
    await state.update_data({"user_id": callback_data.user_id})
    await callback.message.answer("Введите отчество")
    await state.set_state(EditUserStates.patronymic)


@router.message(filters.StateFilter(EditUserStates.patronymic))
async def confirm_patronymic(message: types.Message, state: FSMContext) -> None:
    if not await check_name(message.text):
        await message.answer("Введите корректное отчество")
        return

    state_data = await state.get_data()
    await db.pool.execute(
        """
        UPDATE users SET "patronymic" = $2 WHERE id = $1
        """,
        int(state_data.get("user_id")),
        message.text
    )
    await message.answer("Отчество обновлено")
    await state.set_state(EditUserStates.start)


@router.callback_query(UserCallback.filter(F.action == "email"))
async def prompt_email(callback: types.CallbackQuery, callback_data: UserCallback, state: FSMContext) -> None:
    await state.update_data({"user_id": callback_data.user_id})
    await callback.message.answer("Введите эл. почту")
    await state.set_state(EditUserStates.email)


@router.message(filters.StateFilter(EditUserStates.email))
async def confirm_email(message: types.Message, state: FSMContext) -> None:
    if not await check_email(message.text):
        await message.answer("Введите корректную эл. почту")
        return

    state_data = await state.get_data()
    await db.pool.execute(
        """
        UPDATE users SET "email" = $2 WHERE id = $1
        """,
        int(state_data.get("user_id")),
        message.text
    )
    await message.answer("Эл. почта сохранена")
    await state.set_state(EditUserStates.start)


@router.callback_query(UserCallback.filter(F.action == "password"))
async def prompt_password(callback: types.CallbackQuery, callback_data: UserCallback, state: FSMContext) -> None:
    await state.update_data({"user_id": callback_data.user_id})
    await callback.message.answer("Введите новый пароль")
    await state.set_state(EditUserStates.password)


@router.message(filters.StateFilter(EditUserStates.password))
async def confirm_password(message: types.Message, state: FSMContext) -> None:
    if not await check_password(message.text):
        await message.answer("Введите корректный пароль")
        return

    state_data = await state.get_data()
    await db.pool.execute(
        """
        UPDATE users SET "password" = $2 WHERE id = $1
        """,
        int(state_data.get("user_id")),
        message.text
    )
    await message.answer("Пароль обновлён")
    await state.set_state(EditUserStates.start)


@router.callback_query(UserCallback.filter(F.action == "resume_url"))
async def prompt_resume_url(callback: types.CallbackQuery, callback_data: UserCallback, state: FSMContext) -> None:
    await state.update_data({"user_id": callback_data.user_id})
    await callback.message.answer("Введите ссылку на резюме")
    await state.set_state(EditUserStates.resume_url)


@router.message(filters.StateFilter(EditUserStates.resume_url))
async def confirm_resume_url(message: types.Message, state: FSMContext) -> None:
    if not await check_url(message.text):
        await message.answer("Введите корректную ссылку")
        return

    state_data = await state.get_data()
    await db.pool.execute(
        """
        UPDATE users SET "middlename" = $2 WHERE id = $1
        """,
        int(state_data.get("user_id")),
        message.text
    )
    await message.answer("Ссылка на резюме обновлена")
    await state.set_state(EditUserStates.start)


@router.callback_query(UserCallback.filter(F.action == "letter"))
async def prompt_letter(callback: types.CallbackQuery, callback_data: UserCallback, state: FSMContext) -> None:
    await state.update_data({"letter": callback_data.user_id})
    await callback.message.answer("Введите сопроводительное письмо")
    await state.set_state(EditUserStates.letter)


@router.message(filters.StateFilter(EditUserStates.letter))
async def confirm_letter(message: types.Message, state: FSMContext) -> None:
    if not await check_name(message.text):
        await message.answer("Введите корректное сопроводительное письмо")
        return

    state_data = await state.get_data()
    await db.pool.execute(
        """
        UPDATE letters SET "content" = $1 WHERE id = $2
        """,
        message.text,
        int(state_data.get("user_id")),
    )
    await message.answer("Сопроводительное письмо обновлено")
    await state.set_state(EditUserStates.start)
