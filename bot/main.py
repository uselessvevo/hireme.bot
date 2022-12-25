import asyncio
from contextvars import ContextVar

from bot.loader import dp
from bot.loader import bot
from bot.loader import logger
from core.redis import get_redis


lock = ContextVar("lock")
redis = get_redis()
pubsub = redis.pubsub()


async def get_redis_message(pattern):
    async with lock.get():
        await pubsub.psubscribe(pattern)


async def start_redis_coros():
    lock.set(asyncio.Lock())
    async with pubsub:
        asyncio.create_task(get_redis_message("*:*"))
        async with lock.get():
            await pubsub.subscribe("*:*")

        while True:
            message = await pubsub.get_message(timeout=100)
            logger.info(message)

            if message:
                channel = message.get("channel")
                if channel:
                    channel = channel.decode("utf-8").split(":")
                    if isinstance(message.get("data"), (str, bytes, memoryview)):
                        # Получаем id куратора и пользователя, и отправляем сообщение в чат
                        if len(channel) == 2 and all(str(i).isdigit() for i in channel):
                            curator_id, user_id = list(map(int, channel))
                            await bot.send_message(curator_id, message.get("data"))


def main() -> None:
    logger.info("Starting")
    loop = asyncio.get_event_loop()
    loop.create_task(start_redis_coros())
    loop.create_task(dp.start_polling(bot))
    loop.run_forever()


if __name__ == "__main__":
    main()
