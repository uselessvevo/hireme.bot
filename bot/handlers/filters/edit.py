from aiogram import types
from aiogram import Router
from aiogram import filters
from aiogram.fsm.context import FSMContext

from bot.handlers.users.callbacks import UserCallback
from bot.middlewares import EmployeePermissionMiddleware


router = Router(name="fitlers.edit")
router.message.middleware(EmployeePermissionMiddleware())
router.callback_query.middleware(EmployeePermissionMiddleware())
