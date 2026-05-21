import json
import asyncio

from modules.bot import LobbyBot
from modules.update import Updater
from modules.itemlist import ItemListUpdater


with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)


async def startup_update():

    if not config.get("check_update_on_startup", True):
        return

    updater = Updater()
    await updater.run()

    item_updater = ItemListUpdater(debug=False)
    await item_updater.run()


async def run_bots():

    bots = []

    for i, _ in enumerate(config.get("clients", [])):

        bot = LobbyBot(config, i)
        bots.append(bot)

        asyncio.create_task(bot.start())


async def main():

    await startup_update()

    await run_bots()

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":

    asyncio.run(main())
