from aiogram import types
from aiogram import Router
from aiogram import filters
from aiogram.fsm.context import FSMContext

from core.redis import get_redis
from bot.loader import dp, db


router = Router(name="users.pubsub")


@router.message(filters.Command(commands=["confirm_captcha"]))
async def confirm_captcha(message: types.Message) -> None:
    pass
