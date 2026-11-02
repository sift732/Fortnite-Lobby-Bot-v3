
import json
from typing import Optional, Tuple, Union
from urllib.parse import urljoin

import aiohttp
from packaging import version

__version__ = '0.1.0'

REPOSITORY_URL = 'https://github.com/sift732/Fortnite-Lobby-Bot-v3'
RAW_BASE_URL = 'https://raw.githubusercontent.com/sift732/Fortnite-Lobby-Bot-v3/main/'


class Updater:
    version = __version__

    def __init__(self, bot: 'Bot'):
        self.bot = bot
        self.updates = {}
        self.pc_updates = {}
        self.repl_updates = {}

    def l(self, key: str, *args: tuple, default: Optional[str] = '', **kwargs: dict):
        if hasattr(self.bot, 'l'):
            return self.bot.l(key, *args, default=default, **kwargs)
        return default.format(*args) if args else default

    def add_new_key(self, data: dict, new: dict, overwrite: Optional[bool] = False) -> dict:
        result = data.copy()
        for key, value in new.items():
            if key not in result:
                result[key] = value
            elif isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.add_new_key(result[key], value, overwrite)
            elif overwrite:
                result[key] = value
        return result

    async def check_update(self, uri: str, path: str, save: Optional[str] = None,
                           write: Optional[bool] = True) -> Tuple[bool, Optional[Union[bytes, str]]]:
        if write:
            raise NotImplementedError('File updates are not implemented yet')
        url = urljoin(uri.rstrip('/') + '/', path)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                response.raise_for_status()
                return False, await response.text()

    async def check_updates(self, dev: Optional[bool] = False) -> bool:
        _, content = await self.check_update(RAW_BASE_URL, 'version.json', write=False)
        data = json.loads(content)
        latest_version = data['version']
        if version.parse(__version__) < version.parse(latest_version):
            return True
        return False

    async def update(self, uri: str) -> None:
        raise NotImplementedError('File updates are not implemented yet')