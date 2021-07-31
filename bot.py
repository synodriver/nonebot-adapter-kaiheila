# -*- coding: utf-8 -*-
import nonebot
from nonebot_adapter_kaiheila import Bot as KaiheilaBot

from nonebot.drivers.aiohttp import Driver, WebSocketSetup

nonebot.init(_env_file=".env")
driver: Driver = nonebot.get_driver()
config = driver.config
driver.register_adapter("kaiheila", KaiheilaBot)

nonebot.load_builtin_plugins()

if __name__ == "__main__":
    nonebot.run()
