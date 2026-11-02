
import asyncio
import importlib
import platform
import sys
import traceback

SUPPORT_URL = 'https://discord.com/invite/tfEE7FdDse'

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
        'サードパーティーライブラリの読み込みに失敗しました。'
        '仮想環境に必要なライブラリをインストールしてください。'
    )
    print(f'サポートDiscord: {SUPPORT_URL}')
    print(
        'Failed to load a third-party library. '
        'Install the required packages in the virtual environment.'
    )
    print(f'Support Discord: {SUPPORT_URL}')
    sys.exit(1)

try:
    import modules
except ModuleNotFoundError:
    print(traceback.format_exc())
    print(f'Python {platform.python_version()}\n')
    print(
        'モジュールの読み込みに失敗しました。'
        'プロジェクト内のmodulesディレクトリを確認してください。'
    )
    print(f'サポートDiscord: {SUPPORT_URL}')
    print(
        'Failed to load project modules. '
        'Check the modules directory.'
    )
    print(f'Support Discord: {SUPPORT_URL}')
    sys.exit(1)

if sys.platform == 'win32':
    asyncio.set_event_loop(asyncio.ProactorEventLoop())
else:
    try:
        import uvloop
    except ModuleNotFoundError:
        pass
    else:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

if __name__ == '__main__':
    print(modules.colors.green(
        f'V{modules.__version__}\n'
        f'Python {platform.python_version()}\n'
        f'rebootpy {rebootpy.__version__}\n'
        f'nextcord {nextcord.__version__}\n'
        f'Sanic {sanic.__version__}'
    ))

    
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = modules.Bot('pc', loop=loop)
    bot.setup()
    loop.run_until_complete(bot.start())
