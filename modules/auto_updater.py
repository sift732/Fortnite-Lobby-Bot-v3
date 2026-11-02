import asyncio
import json
import os
from pathlib import Path
from typing import Optional, Tuple, Union
from urllib.parse import urljoin

import aiohttp
from packaging import version

__version__ = '0.1.0'

REPOSITORY_URL = 'https://github.com/sift732/Fortnite-Lobby-Bot-v3'
RAW_BASE_URL = 'https://raw.githubusercontent.com/sift732/Fortnite-Lobby-Bot-v3/main/'
ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / '.update_version.json'


class Updater:
    version = __version__

    def __init__(self, bot: 'Bot'):
        self.bot = bot
        self.updates = {}
        for lang in ('en', 'es', 'ja'):
            for name in ('README', 'commands', 'config', 'custom_commands', 'docs', 'glossary', 'pc', 'repl', 'replies', 'setup'):
                self.updates[f'docs/{lang}/{name}.md'] = []
            self.updates[f'lang/{lang}.json'] = []
        for name in ('__init__', 'auth', 'auto_updater', 'bot', 'client', 'colors', 'commands', 'cosmetics', 'discord_client', 'encoder', 'formatter', 'http', 'localize', 'web', 'webhook'):
            self.updates[f'modules/{name}.py'] = ['backup']
        for name in ('boot-switch', 'clients-viewer', 'clients-viewer-client', 'editor', 'header', 'login', 'main', 'markdown'):
            self.updates[f'statics/css/{name}.css'] = []
        for name in ('boot-switch', 'clients-viewer', 'clients-viewer-client', 'editor', 'header', 'login', 'main', 'ws'):
            self.updates[f'statics/js/{name}.js'] = []
        for name in ('boot-switch', 'clients-viewer', 'clients-viewer-client', 'editor', 'index', 'login', 'openfile'):
            self.updates[f'template/{name}.jinja'] = []
        for name in ('backpack.jpg', 'banner.jpg', 'crown.png', 'emote.jpg', 'favicon.ico', 'logo.png', 'outfit.jpg', 'pickaxe.jpg'):
            self.updates[f'statics/images/{name}'] = ['raw']
        for name in ('commands', 'config', 'custom_commands', 'replies'):
            self.updates[f'{name}.json'] = ['diff', 'backup']
        for name in ('index.py', 'LICENSE', 'README.md', 'README_EN.md', 'README_ES.md', 'requirements.txt'):
            self.updates[name] = ['backup'] if name == 'index.py' else []
        self.pc_updates = {'INSTALL.bat': [], 'RUN.bat': []}
        self.repl_updates = {'pyproject.toml': [], '.replit': [], 'replit.nix': []}

    def l(self, key: str, *args: tuple, default: Optional[str] = '', **kwargs: dict):
        if hasattr(self.bot, 'l'):
            return self.bot.l(key, *args, default=default, **kwargs)
        return default.format(*args) if args else default

    def add_new_key(self, data, new, overwrite=False):
        if isinstance(data, dict) and isinstance(new, dict):
            result = data.copy()
            for key, value in new.items():
                if key not in result:
                    result[key] = value
                elif isinstance(result[key], (dict, list)) and isinstance(value, type(result[key])):
                    result[key] = self.add_new_key(result[key], value, overwrite)
                elif overwrite:
                    result[key] = value
            return result
        if isinstance(data, list) and isinstance(new, list):
            result = list(data)
            for i, value in enumerate(new):
                if i >= len(result):
                    result.append(value)
                elif isinstance(result[i], (dict, list)) and isinstance(value, type(result[i])):
                    result[i] = self.add_new_key(result[i], value, overwrite)
                elif overwrite:
                    result[i] = value
            return result
        return new if overwrite else data

    async def check_update(self, uri: str, path: str, save: Optional[str] = None,
                           write: Optional[bool] = True) -> Tuple[bool, Optional[Union[bytes, str]]]:
        tags = self.updates.get(path, self.pc_updates.get(path, self.repl_updates.get(path)))
        if tags is None:
            raise ValueError(f'Unknown update path: {path}')
        target = ROOT / (save or path)
        url = urljoin(uri.rstrip('/') + '/', path)
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 404:
                    return False, None
                response.raise_for_status()
                latest = await response.read()

        if 'diff' in tags and target.exists():
            try:
                existing_json = json.loads(target.read_text(encoding='utf-8'))
                latest_json = json.loads(latest.decode('utf-8'))
                latest = (json.dumps(self.add_new_key(existing_json, latest_json), ensure_ascii=False, indent=4) + '\n').encode('utf-8')
            except (ValueError, UnicodeError):
                raise ValueError(f'Invalid JSON: {path}')

        existing = target.read_bytes() if target.is_file() else None
        if existing == latest:
            return False, latest

        if write:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and 'backup' in tags:
                backup = target.with_name(f'{target.stem}_old{target.suffix}')
                backup.write_bytes(existing)
            temporary = target.with_name(target.name + '.updating')
            try:
                temporary.write_bytes(latest)
                os.replace(temporary, target)
            finally:
                temporary.unlink(missing_ok=True)
        return True, latest

    async def check_updates(self, dev: Optional[bool] = False) -> bool:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
            async with session.get(urljoin(RAW_BASE_URL, 'version.json')) as response:
                response.raise_for_status()
                data = await response.json(content_type=None)

        latest = str(data['version'])
        current = __version__
        if VERSION_FILE.is_file():
            try:
                installed = str(json.loads(VERSION_FILE.read_text(encoding='utf-8'))['version'])
                if version.parse(installed) > version.parse(current):
                    current = installed
            except (ValueError, KeyError, TypeError):
                pass

        if version.parse(current) >= version.parse(latest):
            return False

        await self.update(RAW_BASE_URL)
        VERSION_FILE.write_text(json.dumps({'version': latest}, indent=4) + '\n', encoding='utf-8')
        return True

    async def update(self, uri: str) -> None:
        paths = dict(self.updates)
        mode = getattr(self.bot, 'mode', None)
        if mode == 'pc':
            paths.update(self.pc_updates)
        elif mode == 'repl':
            paths.update(self.repl_updates)

        failed = []
        for path in paths:
            try:
                await self.check_update(uri, path)
            except (aiohttp.ClientError, asyncio.TimeoutError, OSError, ValueError) as exc:
                failed.append(f'{path}: {exc}')

        if failed:
            raise RuntimeError('Update failed:\n' + '\n'.join(failed))
