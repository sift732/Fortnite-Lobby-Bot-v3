import threading
import asyncio

from modules.bot import LobbyBot
from modules.update import Updater
from modules.itemlist import ItemListUpdater
from modules.web import start_web
import json

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)


async def startup_update():

    if not config.get("check_update_on_startup", True):
        return

    updater = Updater()
    await updater.run()

    item_updater = ItemListUpdater(debug=False)
    await item_updater.run()


def start_web_thread():

    import asyncio
    asyncio.run(start_web())


async def main():

    await startup_update()

    if config.get("web", {}).get("enabled", False):

        threading.Thread(
            target=start_web_thread,
            daemon=True
        ).start()

    for i in range(len(config.get("clients", []))):

        bot = LobbyBot(config, i)
        asyncio.create_task(bot.start())

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":

    asyncio.run(main())
