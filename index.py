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


def run_bots(config):
    bots = []

    for i, _ in enumerate(config.get("clients", [])):
        bot = LobbyBot(config, i)
        bots.append(bot)

        bot.run()


def start():
    asyncio.run(startup_update())
    run_bots(config)


if __name__ == "__main__":
    start()
