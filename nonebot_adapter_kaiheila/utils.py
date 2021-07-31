from typing import BinaryIO

from nonebot.utils import logger_wrapper
import aiohttp

try:
    import ujson as json
except ImportError:
    import json

from .bot import Bot
from .exception import ActionFailed

log = logger_wrapper("Kaiheila")


async def ensure_url(file: BinaryIO, bot: Bot):
    """
    保证上传的是url，使用图床
    """
    data = aiohttp.FormData()
    data.add_field("file", file)
    async with bot.client_session.post(f"{bot.base_url}/asset/create",
                                       data=data,
                                       headers={"Authorization": f"Bot {bot.kaiheila_config.token}"}) as resp:
        ret = await resp.json(loads=json.loads)
        if ret["code"] != 0:
            raise ActionFailed(massage=ret["message"], **(ret["data"]))
        return ret["data"]["url"]
