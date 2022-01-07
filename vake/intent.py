import itertools
import os
import re
import sys
from abc import ABCMeta, abstractmethod
from enum import Enum, auto
from pathlib import Path
from typing import TextIO

from . import config
from . import kernel
from . import locate
from .config import PrefChain, PrefRecipe, PrefBook, SnipRecipe, SnipBook
from .timber import Lumber
from .tty import Color

__all__ = [
    'Action',
    'PrefLinkAction', 'PrefUnlinkAction', 'PrefCleanupAction',
    'PrefListAction', 'PrefListColorOption', 'PrefListStyleOption',
]


# ==
# Base
# ==
class Action(metaclass=ABCMeta):
    @abstractmethod
    def run(self):
        pass


# ==
# Pref
# ==
class PrefAction(Action, metaclass=ABCMeta):
    @staticmethod
    def _recipes(logger: Lumber = Lumber.noop(), noop: bool = False) -> list[PrefRecipe]:
        identity = kernel.identify()

        # shared
        books: list[PrefBook] = [
            config.BinPrefBook(),
            config.ShPrefBook(),
            config.BashPrefBook(),
            config.ZshPrefBook(logger=logger, noop=noop),
            config.VimPrefBook(logger=logger, noop=noop),
            config.GitPrefBook(),
            config.GitHubPrefBook(),
            config.AsdfPrefBook(),
            config.TmuxPrefBook(),
            config.GradlePrefBook(),
        ]

        # linux
        if identity.is_linux():
            books += []

        # darwin
        if identity.is_darwin():
            books += [
                config.BrewPrefBook(logger=logger, noop=noop),
                config.XcodePrefBook(),
                config.IntelliJIdeaPrefBook(),
                config.AndroidStudioPrefBook(),
                config.AppCodePrefBook(),
                config.RubyMinePrefBook(),
                config.GoLandPrefBook(),
                config.CLionPrefBook(),
                config.RiderPrefBook(),
            ]

        return list(itertools.chain(*[book.recipes for book in books]))

    @staticmethod
    def _snippets() -> list[SnipRecipe]:
        books: list[SnipBook] = [
            config.ShSnipBook(),
            config.BashSnipBook(),
            config.ZshSnipBook(),
        ]

        return list(itertools.chain(*[book.recipes for book in books]))

    @staticmethod
    def _test(path: Path):
        blacklist = ['*.swp', '*.bak', '.DS_Store', '.keep', '.gitkeep']

        for pattern in blacklist:
            if path.match(pattern):
                return False

        return True


class PrefLinkAction(PrefAction):
    _cleanup: bool
    _logger: Lumber
    _noop: bool

    def __init__(self, cleanup: bool = True, logger: Lumber = Lumber.noop(), noop: bool = False):
        self._cleanup = cleanup
        self._logger = logger
        self._noop = noop
        return

    def run(self):
        recipes = self._recipes(logger=self._logger, noop=self._noop)

        if self._cleanup:
            PrefCleanupAction(logger=self._logger, noop=self._noop).perform(recipes)

        return self.perform(recipes)

    def perform(self, recipes: list[PrefRecipe]):
        identity = kernel.identify()
        for recipe in recipes:
            if recipe.src.is_absolute():
                chains = recipe.expand()
            else:
                chains = recipe.expand(src_prefix=Path(locate.static(), identity.value)) + \
                         recipe.expand(src_prefix=Path(locate.static(), 'default'))

            for chain in chains:
                self.__link(chain)

            recipe.hook.activate()

        for snippet in self._snippets():
            self.__enable(snippet)

    def __link(self, chain: PrefChain) -> bool:
        if not self._test(chain.src):
            self._logger.debug(f'File ignored: {chain.src}')
            return False

        if not chain.src.exists():
            self._logger.info(f'File not found: {chain.src}')
            return False

        if chain.dst.is_symlink():
            self._logger.info(f'Symlink already exists: {chain.dst}')
            return False

        if chain.dst.is_file():
            self._logger.info(f'File already exists: {chain.dst}')
            return False

        if not chain.dst.parent.is_dir():
            self.__mkdir(chain.dst.parent)

        self.__symlink(chain.src, chain.dst)
        return True

    def __mkdir(self, path: Path) -> bool:
        self._logger.execute(f'mkdir -p {path}')

        if self._noop:
            return False

        path.mkdir(parents=True, exist_ok=True)
        return True

    def __symlink(self, src: Path, dst: Path) -> bool:
        self._logger.execute(f'ln -s -f {src} {dst}')

        if self._noop:
            return False

        dst.symlink_to(src)
        return True

    def __enable(self, snippet: SnipRecipe) -> bool:
        src = Path(locate.snippet(), snippet.src).resolve()
        dst = Path(snippet.dst).expanduser()

        if not src.exists():
            self._logger.info(f'File not found: {snippet.src}')
            return False

        src_str = src.read_text(encoding='utf-8').strip()
        dst_str = dst.read_text(encoding='utf-8').strip() if dst.exists() else ''

        if src_str in dst_str:
            self._logger.info(f'Snippet already enabled: {dst}')
            return False

        self._logger.info(f'Enable snippet: {src}')

        if self._noop:
            return False

        if len(dst_str) > 0:
            new_str = dst_str + os.linesep + src_str + os.linesep
        else:
            new_str = src_str + os.linesep

        dst.write_text(new_str, encoding='utf-8')
        return True


class PrefUnlinkAction(PrefAction):
    _cleanup: bool
    _logger: Lumber
    _noop: bool

    def __init__(self, cleanup: bool = True, logger: Lumber = Lumber.noop(), noop: bool = False):
        self._cleanup = cleanup
        self._logger = logger
        self._noop = noop
        return

    def run(self):
        recipes = self._recipes(logger=self._logger, noop=self._noop)

        if self._cleanup:
            PrefCleanupAction(logger=self._logger, noop=self._noop).perform(recipes)

        return self.perform(recipes)

    def perform(self, recipes: list[PrefRecipe]):
        identity = kernel.identify()

        for recipe in recipes:
            if recipe.src.is_absolute():
                chains = recipe.expand()
            else:
                chains = recipe.expand(src_prefix=Path(locate.static(), identity.value)) + \
                         recipe.expand(src_prefix=Path(locate.static(), 'default'))

            for chain in chains:
                self.__unlink(chain)

            recipe.hook.deactivate()

        for snippet in self._snippets():
            self.__disable(snippet)

        return

    def __unlink(self, chain: PrefChain) -> bool:
        if not self._test(chain.src):
            self._logger.debug(f'File is not target: {chain.src}')
            return False

        if not chain.src.exists():
            self._logger.info(f'File not found: {chain.src}')
            return False

        if not chain.dst.exists() and not chain.dst.is_symlink():
            self._logger.info(f'File already removed: {chain.dst}')
            return True

        return self.__rm(chain.dst)

    def __rm(self, path: Path) -> bool:
        self._logger.execute(f'rm -f {path}')

        if self._noop:
            return False

        path.unlink(missing_ok=True)
        return True

    def __disable(self, snippet: SnipRecipe) -> bool:
        src = Path(locate.snippet(), snippet.src).resolve()
        dst = Path(snippet.dst).expanduser()

        if not src.exists():
            self._logger.info(f'File not found: {src}')
            return False

        if not dst.exists():
            self._logger.info(f'File not found: {dst}')
            return False

        src_str = src.read_text(encoding='utf-8').strip()
        dst_str = dst.read_text(encoding='utf-8')

        if src_str not in dst_str:
            self._logger.info(f'Snippet already disabled: {dst}')
            return False

        self._logger.info(f'Disable snippet: {src}')

        if self._noop:
            return False

        pattern = re.escape(src_str) + os.linesep + '*'
        new_str = re.sub(pattern, '', dst_str)
        dst.write_text(new_str, encoding='utf-8')
        return True


class PrefListColorOption(Enum):
    AUTO = 'auto'
    ALWAYS = 'always'
    NEVER = 'never'


class PrefListStyleOption(Enum):
    SHORT = auto()
    LONG = auto()


class PrefListAction(PrefAction):
    _stream: TextIO
    _color: PrefListColorOption
    _style: PrefListStyleOption

    def __init__(self,
                 stream: TextIO = sys.stdout,
                 color: PrefListColorOption = PrefListColorOption.AUTO,
                 style: PrefListStyleOption = PrefListStyleOption.SHORT):
        self._stream = stream
        self._color = color
        self._style = style

    def run(self):
        identity = kernel.identify()
        recipes = self._recipes(logger=Lumber.noop(), noop=False)

        chains: list[PrefChain] = []

        for recipe in recipes:
            if recipe.src.is_absolute():
                chains += recipe.expand()
            else:
                chains += recipe.expand(src_prefix=Path(locate.static(), identity.value))
                chains += recipe.expand(src_prefix=Path(locate.static(), 'default'))

        chains.sort(key=lambda x: x.dst)
        lines = [self.__line(x) for x in chains if self._test(x.src)]

        self._stream.writelines(lines)
        return

    def __line(self, chain: PrefChain, sep: str = ' -> ', end: str = os.linesep) -> str:
        cwd = Path.cwd()

        src = chain.src.relative_to(cwd) if chain.src.is_relative_to(cwd) else chain.src
        dst = chain.dst if chain.dst.exists() else Path('(null)')

        if self._color == PrefListColorOption.ALWAYS:
            colorized = True
        elif self._color == PrefListColorOption.NEVER:
            colorized = False
        elif self._color == PrefListColorOption.AUTO:
            colorized = self._stream.isatty()
        else:
            colorized = self._stream.isatty()

        if colorized:
            color = self.__color(dst)

            if self._style == PrefListStyleOption.LONG:
                pair = (
                    color.decorate(dst),
                    str(src),
                )
            elif self._style == PrefListStyleOption.SHORT:
                pair = (
                    color.decorate(dst),
                )
            else:
                pair = (
                    color.decorate(dst),
                )

            return sep.join(pair) + end
        else:
            if self._style == PrefListStyleOption.LONG:
                pair = (
                    str(dst),
                    str(src),
                )
            elif self._style == PrefListStyleOption.SHORT:
                pair = (
                    str(dst),
                )
            else:
                pair = (
                    str(dst),
                )

            return sep.join(pair) + end

    @staticmethod
    def __color(path: Path) -> Color:
        if not path.exists():
            return Color.RED
        elif path.is_symlink():
            return Color.MAGENTA
        elif path.is_dir():
            return Color.BLUE
        elif path.is_file():
            return Color.RESET
        else:
            return Color.RESET


class PrefCleanupAction(PrefAction):
    _logger: Lumber
    _noop: bool

    def __init__(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        self._logger = logger
        self._noop = noop
        return

    def run(self):
        recipes = self._recipes(logger=self._logger, noop=self._noop)
        return self.perform(recipes)

    def perform(self, recipes: list[PrefRecipe]):
        paths = [recipe.dst.expanduser() for recipe in recipes if not recipe.private]
        paths.sort()

        found: list[Path] = []

        for path in paths:
            message = f'Scanning {path}'
            self._logger.debug(f'{message}...\r', terminate=False)
            found += self.__scan(path)
            self._logger.debug(f'{message}... Done')

        self._logger.debug(f'Found {len(found)} broken symlinks')
        for path in found:
            self.__rm(path)

        return

    @staticmethod
    def __scan(path: Path) -> list[Path]:
        if path.is_symlink() and not path.exists():
            return [path]

        if not path.exists():
            return []

        if path.is_file():
            return []

        if path.is_dir():
            return [
                x for x
                in path.glob('**/*')
                if x.is_symlink() and not x.exists()
            ]

        return []

    def __rm(self, path: Path) -> bool:
        self._logger.execute(f'rm -f {path}')

        if self._noop:
            return False

        path.unlink(missing_ok=True)
        return True
