import logging
import asyncio
from aiogram import Bot, Dispatcher

from core import config


def setup_database() -> "Database":
    from core.database import Database

    loop = asyncio.get_event_loop()
    database = Database(loop)
    return database


def setup_dispatcher() -> Dispatcher:
    from bot.handlers.start import router as start_router
    from bot.handlers.users.main import router as users_router
    from bot.handlers.users.create import router as user_register_router
    from bot.handlers.users.edit import router as user_edit_router

    from bot.handlers.filters.create import router as filter_create_router
    from bot.handlers.filters.edit import router as filter_edit_router

    from bot.handlers.search.main import router as search_main_router

    dispatcher = Dispatcher()
    # Replace it with automatic router
    # detector with `exclude` or `only` parameter
    dispatcher.include_router(start_router)
    dispatcher.include_router(users_router)
    dispatcher.include_router(user_register_router)
    dispatcher.include_router(user_edit_router)

    dispatcher.include_router(filter_create_router)
    dispatcher.include_router(filter_edit_router)

    dispatcher.include_router(search_main_router)

    return dispatcher


def setup_bot() -> Bot:
    return Bot(token=config.BOT_TOKEN)


logging.basicConfig(
    level='INFO',
    format="%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

db = setup_database()
dp = setup_dispatcher()
bot = setup_bot()
