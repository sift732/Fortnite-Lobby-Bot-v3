import json
import asyncio

from modules.bot import run_bots
from modules.update import Updater


with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)


async def startup_update():
    if not config.get("check_update_on_startup", True):
        return

    updater = Updater()
    await updater.run()


def start():
    asyncio.run(startup_update())
    run_bots(config)


if __name__ == "__main__":
    start()
