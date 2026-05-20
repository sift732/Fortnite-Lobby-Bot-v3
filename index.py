import json
import asyncio

from rebootpy import Client

from modules.auth import MyAdvancedAuth
from modules import translate
from utils import color
from utils.logger import Logger
from modules.update import Updater

color.init()
translate.load_lang()

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

client = Client(auth=MyAdvancedAuth())


async def startup_update():
    updater = Updater(client)

    if config["check_update_on_startup"] is False:
        return

    await updater.run()


@client.event
async def event_device_code_generated(link):
    Logger.info(
        translate.get(
            "main.confirm_authorization",
            link,
            "Epic Games"
        )
    )


@client.event
async def event_ready():
    Logger.success(
        translate.get(
            "client.ready",
            client.user
        )
    )


async def main():
    await startup_update()


asyncio.run(main())

client.run()
