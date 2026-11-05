import asyncio
import importlib
import os
import platform
import sys
import traceback

try:
    import aiohttp
    import colorama
    import jaconv
    import sanic

    nextcord = importlib.import_module('nextcord')
    rebootpy = importlib.import_module('rebootpy')
    pykakasi = importlib.import_module('pykakasi')
except ModuleNotFoundError:
    print(traceback.format_exc())
    print(f'Python {platform.python_version()}\n')
    print(
        'サードパーティーライブラリの読み込みに失敗しました。INSTALL を実行してください。\n'
        'Twitter @qwxia_\n'
        'Discord @qwxia.\n'
        'GitHub https://github.com/sift732/Fortnite-Lobby-Bot-v3\n'
        'Discordサーバー https://discord.gg/tfEE7FdDse'
    )
    print('\n')
    print(
        'Failed to load third-party libraries. Please run INSTALL.\n'
        'Twitter @qwxia_\n'
        'Discord @qwxia.\n'
        'GitHub https://github.com/sift732/Fortnite-Lobby-Bot-v3\n'
        'Discord Server https://discord.gg/tfEE7FdDse'
    )
    sys.exit(1)

try:
    import modules
except ModuleNotFoundError:
    print(traceback.format_exc())
    print(f'Python {platform.python_version()}\n')
    print(
        'モジュールの読み込みに失敗しました。Check Update.bat を実行してください。\n'
        'Twitter @qwxia_\n'
        'Discord @qwxia.\n'
        'GitHub https://github.com/sift732/Fortnite-Lobby-Bot-v3\n'
        'Discordサーバー https://discord.gg/tfEE7FdDse'
    )
    print('\n')
    print(
        'Failed to load modules. Please run Check Update.bat.\n'
        'Twitter @qwxia_\n'
        'Discord @qwxia.\n'
        'GitHub https://github.com/sift732/Fortnite-Lobby-Bot-v3\n'
        'Discord Server https://discord.gg/tfEE7FdDse'
    )
    sys.exit(1)

if __name__ == '__main__':
    dev = '-dev' in sys.argv

    if (os.getenv('RAILWAY_ENVIRONMENT') is not None
            and sys.platform == 'linux'):
        mode = 'railway'
    elif (os.getenv('REPLIT_DB_URL') is not None
            and os.getcwd().startswith('/home/runner')
            and sys.platform == 'linux'):
        mode = 'repl'
    else:
        mode = 'pc'

    print(modules.colors.green(
        f'V{modules.__version__}\n'
        f'Python {platform.python_version()}\n'
        f'rebootpy {rebootpy.__version__}\n'
        f'nextcord {nextcord.__version__}\n'
        f'Sanic {sanic.__version__}'
    ))

    if sys.platform == 'win32':
        loop = asyncio.new_event_loop()
    else:
        try:
            import uvloop
        except ModuleNotFoundError:
            loop = asyncio.new_event_loop()
        else:
            loop = uvloop.new_event_loop()

    asyncio.set_event_loop(loop)

    async def main():
        bot = modules.Bot(
            mode,
            loop=asyncio.get_running_loop()
        )
        bot.dev = dev
        bot.setup()
        await bot.start()

    try:
        loop.run_until_complete(main())
    finally:
        if not loop.is_closed():
            loop.close()
