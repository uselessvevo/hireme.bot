import aioredis
from core.config import REDIS_PROT, REDIS_HOST, REDIS_PORT


def get_redis() -> aioredis.StrictRedis:
    return aioredis.from_url("%s://%s:%s" % (REDIS_PROT, REDIS_HOST, REDIS_PORT))
