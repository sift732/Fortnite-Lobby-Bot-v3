
import io
import sys
from typing import Callable, Optional

from . import colors
from .auto_updater import __version__
from .bot import *
from .colors import init, red

init()


class MyStream(io.StringIO):
    def __init__(
        self,
        original: io.IOBase,
        func: Optional[Callable] = None
    ) -> None:
        self.original = original
        self.func = func if func is not None else (lambda x: x)
        super().__init__()

    def write(self, s: str) -> int:
        s = self.func(s)
        print(s, end='', file=self.original)
        return super().write(s)

    def read(self, size: Optional[int] = -1) -> str:
        self.seek(0)
        return super().read(size)


sys.stdout = MyStream(sys.stdout)
sys.stderr = MyStream(sys.stderr, red)
