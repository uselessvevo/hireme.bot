import aiohttp
from core import config


async def make_scrapper_request(curator_id: int, user_id: int) -> None:
    """
    Call Scrapper Web API

    Args:
        curator_id (int): curator id
        user_id (int): user id
    """
    params = {"curator_id": curator_id, "user_id": user_id}

    async with aiohttp.ClientSession() as client:
        await client.get("%s/%s" % (config.SCRAPPER_URL, ""), params=params)
