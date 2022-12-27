import json

import aiohttp
from core import config


async def request_start_task(curator_id: int, user_id: int) -> aiohttp.ClientResponse:
    """
    Call Scrapper Web API

    Args:
        curator_id (int): curator id
        user_id (int): user id

    TODO: Replace arguments with `User` model
    """
    params = {"curator_id": curator_id, "user_id": user_id}

    async with aiohttp.ClientSession() as client:
        async with client.post("%s/%s" % (config.SCRAPPER_URL, "start-task"), data=json.dumps(params)) as respone:
            return respone
