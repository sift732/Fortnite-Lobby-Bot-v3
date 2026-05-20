import json
import asyncio

from rebootpy import Client

from modules.auth import MyAdvancedAuth
from modules import translate
from utils import color
from utils.logger import Logger
from modules.update import run_update

color.init()
translate.load_lang()

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

client = Client(auth=MyAdvancedAuth())


async def startup_update():
    if not config.get("check_update_on_startup", True):
        return

    await run_update()


@client.event
async def event_device_code_generated(link):
    Logger.info(
        translate.get("main.confirm_authorization", link)
    )


@client.event
async def event_ready():
    Logger.success(
        translate.get("client.ready", client.user)
    )


def start():
    asyncio.run(startup_update())
    client.run()


if __name__ == "__main__":
    start()

#test
