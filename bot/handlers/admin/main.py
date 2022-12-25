from aiogram import F
from aiogram import types
from aiogram import Router
from aiogram import filters
from aiogram.fsm.context import FSMContext

from bot.handlers.users.callbacks import UserCallback
from bot.loader import dp, db
from core.redis import get_redis


router = Router(name="admin.main")


@router.message(filters.Command(commands=["admin_menu"]))
async def admin_menu(message: types.Message, state: FSMContext) -> None:
    pass
