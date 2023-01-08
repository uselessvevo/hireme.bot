from aiogram import types
from aiogram import Router
from aiogram import filters

from bot.loader import db
from bot.handlers.users.structs import RESPONSE_MAPPING
from bot.middlewares import EmployeePermissionMiddleware

router = Router(name="users.chat")
router.message.middleware(EmployeePermissionMiddleware(role="is_admin"))
router.callback_query.middleware(EmployeePermissionMiddleware(role="is_admin"))
