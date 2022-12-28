import json

import aiohttp
from core import config


async def request_start_task(curator_id: int, user_id: int) -> aiohttp.ClientResponse:
    """
    Prepare and start scrapper task

    Args:
        curator_id (int): curator id
        user_id (int): user id

    Returns:
        aiohttp.ClientResponse
    """
    params: dict = {"curator_id": curator_id, "user_id": user_id}

    async with aiohttp.ClientSession() as client:
        async with client.post("%s/%s" % (config.SCRAPPER_URL, "start-task"), data=json.dumps(params)) as response:
            return response


async def request_get_active_tasks(curator_id: int = None, user_id: int = None) -> aiohttp.ClientResponse:
    """
    Get all active tasks or filter by `curator:user` pair

    Args:
        curator_id (int): curator id
        user_id (int): user id

    Returns:
        aiohttp.ClientResponse
    """
    params: dict = {"curator_id": curator_id, "user_id": user_id}

    async with aiohttp.ClientSession() as client:
        async with client.get("%s/%s" % (config.SCRAPPER_URL, "active-tasks"), params=params) as response:
            return response
