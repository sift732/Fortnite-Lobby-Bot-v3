import asyncio
import json
import os
import re
import sys
from typing import TYPE_CHECKING, Optional, Tuple, Union

from aiofiles import open as aopen
from aiofiles.os import replace as areplace
from packaging import version

from .localize import LocalizedText

if TYPE_CHECKING:
    from .bot import Bot


__version__ = '3.0.2'
class Updater:
    version = __version__

    def __init__(self, bot: 'Bot'):
        self.bot = bot
        self._update_backups = set()
        self._failed_backups = set()
        self.protected_json = ('config.json', 'commands.json', 'custom_commands.json', 'replies.json')
        self.updates = {
            'docs/en/commands.md': [],
            'docs/en/config.md': [],
            'docs/en/custom_commands.md': [],
            'docs/en/docs.md': [],
            'docs/en/glossary.md': [],
            'docs/en/pc.md': [],
            'docs/en/repl.md': [],
            'docs/en/replies.md': [],
            'docs/en/setup.md': [],

            'docs/ja/commands.md': [],
            'docs/ja/config.md': [],
            'docs/ja/custom_commands.md': [],
            'docs/ja/docs.md': [],
            'docs/ja/glossary.md': [],
            'docs/ja/pc.md': [],
            'docs/ja/repl.md': [],
            'docs/ja/replies.md': [],
            'docs/ja/setup.md': [],

            'lang/en.json': [],
            'lang/es.json': [],
            'lang/ja.json': [],

            'modules/__init__.py': ['backup'],
            'modules/auth.py': ['backup'],
            'modules/auto_updater.py': ['backup'],
            'modules/bot.py': ['backup'],
            'modules/client.py': ['backup'],
            'modules/colors.py': ['backup'],
            'modules/commands.py': ['backup'],
            'modules/cosmetics.py': ['backup'],
            'modules/discord_client.py': ['backup'],
            'modules/encoder.py': ['backup'],
            'modules/formatter.py': ['backup'],
            'modules/http.py': ['backup'],
            'modules/localize.py': ['backup'],
            'modules/web.py': ['backup'],
            'modules/webhook.py': ['backup'],

            'static/css/boot-switch.css': [],
            'static/css/clients-viewer.css': [],
            'static/css/clients-viewer-client.css': [],
            'static/css/editor.css': [],
            'static/css/header.css': [],
            'static/css/login.css': [],
            'static/css/main.css': [],
            'static/css/markdown.css': [],

            'static/images/backpack.jpg': ['raw'],
            'static/images/banner.jpg': ['raw'],
            'static/images/crown.png': ['raw'],
            'static/images/emote.jpg': ['raw'],
            'static/images/favicon.ico': ['raw'],
            'static/images/logo.png': ['raw'],
            'static/images/outfit.jpg': ['raw'],
            'static/images/pickaxe.jpg': ['raw'],

            'static/js/boot-switch.js': [],
            'static/js/clients-viewer.js': [],
            'static/js/clients-viewer-client.js': [],
            'static/js/editor.js': [],
            'static/js/header.js': [],
            'static/js/login.js': [],
            'static/js/main.js': [],
            'static/js/ws.js': [],

            'templates/index.jinja': [],
            'templates/login.jinja': [],
            'templates/editor.jinja': [],
            'templates/boot-switch.jinja': [],
            'templates/clients-viewer.jinja': [],

            'index.py': ['backup'],
            'LICENSE': [],
            'README.md': [],
            'README_EN.md': [],
            'README_ES.md': [],
            'requirements.txt': []
        }
        self.pc_updates = {
            'INSTALL.bat': [],
            'RUN.bat': []
        }
        self.repl_updates = {
            'pyproject.toml': [],
            '.replit': []
        }

    def l(self, key: str, *args: tuple, default: Optional[str] = '', **kwargs: dict) -> LocalizedText:
        return LocalizedText(self.bot, ['main', key], default, *args, **kwargs)

    async def check_update(self, uri: str, path: str, save: Optional[str] = None,
                           write: Optional[bool] = True) -> Tuple[bool, Optional[Union[bytes, str]]]:
        if path in self.protected_json:
            return False, None
        dirs = '/'.join(path.split('/')[:-1])
        dirs = f'{dirs}/' if dirs else ''
        filename = path.split('/')[-1]
        key = '.'.join(filename.split('.')[:-1])
        extension = filename.split('.')[-1]
        tags = self.updates.get(path, self.pc_updates.get(path, self.repl_updates.get(path, [])))
        save = save or path
        is_image = (
            True
            if path.endswith('.png') or path.endswith('.jpg') or path.endswith('.ico') else
            False
        )

        async def backup():
            if os.path.isfile(path) and 'backup' in tags:
                try:
                    backup_path = f'{dirs}{key}_old.{extension}'
                    if os.path.isfile(backup_path):
                        raise RuntimeError(f'Backup already exists: {backup_path}')
                    await areplace(path, backup_path)
                    self._update_backups.add(backup_path)
                except PermissionError:
                    self.bot.send(
                        self.l(
                            'backup_failed',
                            path,
                            default=(
                                "'{0}' のバックアップに失敗しました\n"
                                "Failed backup for '{0}'"
                            )
                        ),
                        add_p=self.bot.time
                    )

        self.bot.send(
            self.l(
                'checking_update',
                path,
                default=(
                    "'{0}' のアップデートを確認中...\n"
                    "Checking update for '{0}'..."
                )
            ),
            add_p=[self.bot.time, lambda x: f'\n{x}']
        )
        retry = 5
        for tries in range(retry):
            if 'db' in tags:
                if self.bot.isfile(key):
                    existing = await self.bot.aload_json(key)
                else:
                    existing = {}
            else:
                if os.path.isfile(path):
                    if 'raw' in tags:
                        async with aopen(path, 'rb') as f:
                            existing = await f.read()
                            if not is_image and sys.platform == 'win32':
                                existing = existing.replace(b'\r\n', b'\n')
                    else:
                        async with aopen(path, 'r', encoding='utf-8') as f:
                            existing = await f.read()
                            if not is_image and sys.platform == 'win32':
                                existing = existing.replace('\r\n', '\n')
                else:
                    existing = b'' if 'raw' in tags else ''
            try:
                res = await self.bot.http.session.get(uri + path)
            except (OSError, asyncio.TimeoutError):
                if tries + 1 == retry:
                    raise RuntimeError(f"Failed to download {path}")
                await asyncio.sleep(10)
                continue
            if res.status == 404:
                res.release()
                self.bot.send(
                    self.l(
                        'file_not_found',
                        path,
                        default=(
                            "'{0}' ファイルが存在しません\n"
                            "File '{0}' doesn't exists"
                        )
                    ),
                    add_p=self.bot.time
                )
                raise RuntimeError(f"File not found: {path}")
            if res.status != 200:
                retry_after = 10
                res.release()
                self.bot.send(
                    self.l(
                        'get_failed',
                        path,
                        retry_after,
                        tries,
                        retry,
                        default=(
                            "'{0}' のデータの取得に失敗しました。{1}秒後に再試行します {2}/{3}\n"
                            "Failed to get data for '{0}'. Retry after {1} seconds {2}/{3}"
                        )
                    ),
                    add_p=self.bot.time
                )
                if tries + 1 == retry:
                    raise RuntimeError(f"HTTP {res.status}: {path}")
                await asyncio.sleep(retry_after)
                continue

            if path.endswith('.json'):
                latest = await res.json(content_type=None)
                res.release()
                if not isinstance(latest, (dict, list)):
                    raise ValueError(f'Invalid JSON data: {path}')
                if isinstance(existing, str) and existing:
                    existing = json.loads(existing)
                if existing != latest:
                    if write:
                        if dirs:
                            os.makedirs(dirs, exist_ok=True)
                        await backup()
                        async with aopen(save, 'w', encoding='utf-8') as f:
                            await f.write(json.dumps(latest, ensure_ascii=False, indent=4) + '\n')
                        self.bot.send(self.l('update_detected', path), add_p=self.bot.time)
                    return True, latest
            else:
                if 'raw' in tags:
                    latest = await res.read()
                    if not is_image and sys.platform == 'win32':
                        latest = latest.replace(b'\r\n', b'\n')
                else:
                    latest = await res.text()
                    if not is_image and sys.platform == 'win32':
                        latest = latest.replace('\r\n', '\n')
                res.release()

                if existing != latest:
                    if write:
                        self.bot.send(
                            self.l(
                                'update_detected',
                                path,
                                default=(
                                    "'{0}' のアップデートを確認しました\n"
                                    "Detected update for '{0}'"
                                )
                            ),
                            add_p=self.bot.time
                        )
                        if dirs:
                            os.makedirs(dirs, exist_ok=True)
                        await backup()
                        if 'raw' in tags:
                            async with aopen(save, 'wb') as f:
                                await f.write(latest)
                        else:
                            async with aopen(save, 'w', encoding='utf-8') as f:
                                await f.write(latest)
                    return True, latest
            return False, latest

    async def cleanup_protected_json(self) -> None:
        for path in self.protected_json:
            backup = path.removesuffix('.json') + '_old.json'
            if not os.path.isfile(backup):
                continue
            try:
                if not os.path.isfile(path):
                    async with aopen(backup, 'r', encoding='utf-8') as source:
                        content = await source.read()
                    if not isinstance(json.loads(content), (dict, list)):
                        raise ValueError(f'Invalid JSON root: {backup}')
                    os.replace(backup, path)
                else:
                    os.remove(backup)
            except (OSError, UnicodeError, ValueError) as exc:
                print(f'Protected JSON cleanup failed for {path}: {exc}', file=sys.stderr)

    async def check_updates(self, dev: Optional[bool] = False) -> bool:
        branch = 'dev' if dev else 'main'
        uri = f'https://raw.githubusercontent.com/sift732/Fortnite-Lobby-Bot-v3/{branch}/'

        await self.cleanup_protected_json()

        try:
            async with self.bot.http.session.get(f'{uri}version.json') as res:
                if res.status != 200:
                    raise RuntimeError(f'HTTP {res.status}: version.json')
                data = await res.json(content_type=None)

            remote_version = data['version']
            if not isinstance(remote_version, str):
                raise ValueError('Invalid version')
            if version.parse(self.version) >= version.parse(remote_version):
                return False

            self.bot.send(
                self.l('new_version', remote_version),
                add_p=self.bot.time
            )

            await self.update(uri)
            await self.write_version(remote_version)
            await self.cleanup_backups()


        except (OSError, asyncio.TimeoutError, ValueError, TypeError, KeyError, RuntimeError) as exc:
            print(f"Update failed: {exc}", file=sys.stderr)
            return False

        self.bot.send(
            self.l('update_finish', remote_version),
            add_p=[self.bot.time, lambda x: f'\n{x}']
        )
        return True

    async def write_version(self, remote_version: str) -> None:
        path = os.path.abspath(__file__)
        async with aopen(path, 'r', encoding='utf-8') as f:
            source = await f.read()

        pattern = r"(?m)^__version__\s*=\s*(['\"])[^'\"\r\n]*\1\s*$"
        updated, count = re.subn(
            pattern,
            lambda match: f"__version__ = '{remote_version}'",
            source,
            count=1
        )
        if count != 1:
            raise RuntimeError('Version declaration not found')

        temporary = f'{path}.tmp'
        try:
            async with aopen(temporary, 'w', encoding='utf-8') as f:
                await f.write(updated)
            await areplace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.remove(temporary)
                
    async def cleanup_backups(self) -> None:
        for backup_path in tuple(self._update_backups):
            if backup_path in self._failed_backups:
                continue
            if os.path.isfile(backup_path):
                os.remove(backup_path)
            self._update_backups.discard(backup_path)

    async def update(self, uri: str) -> None:
        self._update_backups.clear()
        self._failed_backups.clear()
        semaphore = asyncio.Semaphore(10)

        async def update_file(path: str) -> None:
            async with semaphore:
                dirs = '/'.join(path.split('/')[:-1])
                dirs = f'{dirs}/' if dirs else ''
                filename = path.split('/')[-1]
                key = '.'.join(filename.split('.')[:-1])
                extension = filename.split('.')[-1]
                backup_path = f'{dirs}{key}_old.{extension}'
                try:
                    await self.check_update(uri, path)
                except Exception:
                    if backup_path in self._update_backups:
                        self._failed_backups.add(backup_path)
                        if os.path.isfile(backup_path):
                            try:
                                async with aopen(backup_path, 'rb') as source:
                                    original = await source.read()
                                async with aopen(path, 'wb') as target:
                                    await target.write(original)
                            except Exception as restore_error:
                                print(f'Restore failed for {path}: {restore_error}', file=sys.stderr)
                    raise

        paths = [path for path in self.updates if path != 'modules/auto_updater.py' and path not in self.protected_json]

        if self.bot.mode == 'pc':
            paths.extend(self.pc_updates)
        elif self.bot.mode == 'repl':
            paths.extend(self.repl_updates)

        results = await asyncio.gather(
            *(update_file(path) for path in paths),
            return_exceptions=True
        )
        failures = [(path, result) for path, result in zip(paths, results) if isinstance(result, BaseException)]
        if failures:
            for path, error in failures:
                print(f'Update failed for {path}: {error}', file=sys.stderr)
            raise RuntimeError(f'{len(failures)} file update(s) failed')
