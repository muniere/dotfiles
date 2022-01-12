import os
import re
import sys
from abc import ABCMeta, abstractmethod
from enum import Enum, auto
from pathlib import Path
from typing import TextIO

from . import _
from . import config
from . import kernel
from . import locate
from .config import PrefChain, CookBook, SnipRecipe
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
    def _books(logger: Lumber = Lumber.noop(), noop: bool = False, reverse: bool = False) -> list[CookBook]:
        identity = kernel.identify()

        # shared
        core_books: list[CookBook] = [
            config.BinCookBook(),
            config.ShCookBook(),
            config.BashCookBook(),
            config.ZshCookBook(logger=logger, noop=noop),
            config.VimCookBook(logger=logger, noop=noop),
            config.GitCookBook(),
            config.GitHubCookBook(),
            config.AsdfCookBook(),
            config.TmuxCookBook(),
            config.RangerCookBook(),
            config.GradleCookBook(),
        ]

        pre_books: list[CookBook] = []
        post_books: list[CookBook] = []

        # linux
        if identity.is_linux():
            pre_books += []
            post_books += []

        # darwin
        if identity.is_darwin():
            pre_books += [
                config.BrewCookBook(logger=logger, noop=noop),
            ]
            post_books += [
                config.XcodeCookBook(),
                config.IntelliJIdeaCookBook(),
                config.AndroidStudioCookBook(),
                config.AppCodeCookBook(),
                config.RubyMineCookBook(),
                config.GoLandCookBook(),
                config.CLionCookBook(),
                config.RiderCookBook(),
            ]

        books = pre_books + core_books + post_books

        if reverse:
            return list(reversed(books))
        else:
            return list(books)

    @staticmethod
    def _test(path: Path):
        blacklist = ['*.swp', '*.bak', '.DS_Store', '.keep', '.gitkeep']

        for pattern in blacklist:
            if path.match(pattern):
                return False

        return True


class PrefLinkAction(PrefAction):
    _cleanup: bool
    _activate: bool
    _logger: Lumber
    _noop: bool

    def __init__(self,
                 cleanup: bool = True,
                 activate: bool = True,
                 logger: Lumber = Lumber.noop(),
                 noop: bool = False):
        self._cleanup = cleanup
        self._activate = activate
        self._logger = logger
        self._noop = noop
        return

    def run(self):
        books = self._books(logger=self._logger, noop=self._noop, reverse=False)

        if self._cleanup:
            PrefCleanupAction(logger=self._logger, noop=self._noop).perform(books)

        return self.perform(books)

    def perform(self, books: list[CookBook]):
        identity = kernel.identify()

        for book in books:
            for recipe in book.recipes:
                if recipe.src.is_absolute():
                    chains = recipe.expand()
                else:
                    chains = recipe.expand(src_prefix=Path(locate.static(), identity.value)) + \
                             recipe.expand(src_prefix=Path(locate.static(), 'default'))

                for chain in chains:
                    self.__link(chain)

            for snippet in book.snippets:
                self.__enable(snippet)

            if self._activate:
                book.activate()

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
        self._logger.trace(f'mkdir -p {path}')

        if self._noop:
            return False

        path.mkdir(parents=True, exist_ok=True)
        return True

    def __symlink(self, src: Path, dst: Path) -> bool:
        self._logger.trace(f'ln -s -f {src} {dst}')

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

        new_str = _.box(len(dst_str)).fold(
            some=lambda: dst_str + os.linesep + src_str + os.linesep,
            none=lambda: src_str + os.linesep,
        )

        dst.write_text(new_str, encoding='utf-8')
        return True


class PrefUnlinkAction(PrefAction):
    _cleanup: bool
    _deactivate: bool
    _logger: Lumber
    _noop: bool

    def __init__(self,
                 cleanup: bool = True,
                 deactivate: bool = True,
                 logger: Lumber = Lumber.noop(),
                 noop: bool = False):
        self._cleanup = cleanup
        self._deactivate = deactivate
        self._logger = logger
        self._noop = noop
        return

    def run(self):
        books = self._books(logger=self._logger, noop=self._noop, reverse=True)

        if self._cleanup:
            PrefCleanupAction(logger=self._logger, noop=self._noop).perform(books)

        return self.perform(books)

    def perform(self, books: list[CookBook]):
        identity = kernel.identify()

        for book in books:
            if self._deactivate:
                book.deactivate()

            for snippet in book.snippets:
                self.__disable(snippet)

            for recipe in book.recipes:
                if recipe.src.is_absolute():
                    chains = recipe.expand()
                else:
                    chains = recipe.expand(src_prefix=Path(locate.static(), identity.value)) + \
                             recipe.expand(src_prefix=Path(locate.static(), 'default'))

                for chain in chains:
                    self.__unlink(chain)

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
        self._logger.trace(f'rm -f {path}')

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

    SEP = ' -> '
    END = os.linesep

    def __init__(self,
                 stream: TextIO = sys.stdout,
                 color: PrefListColorOption = PrefListColorOption.AUTO,
                 style: PrefListStyleOption = PrefListStyleOption.SHORT):
        self._stream = stream
        self._color = color
        self._style = style

    def run(self):
        identity = kernel.identify()
        books = self._books(logger=Lumber.noop(), noop=False)

        chains: list[PrefChain] = []

        for book in books:
            for recipe in book.recipes:
                if recipe.src.is_absolute():
                    chains += recipe.expand()
                else:
                    chains += recipe.expand(src_prefix=Path(locate.static(), identity.value))
                    chains += recipe.expand(src_prefix=Path(locate.static(), 'default'))

        chains.sort(key=lambda x: x.dst)
        lines = [self.__line(x) for x in chains if self._test(x.src)]

        self._stream.writelines(lines)
        return

    def __line(self, chain: PrefChain) -> str:
        if self.__colorful():
            return self.__line_colored(chain)
        else:
            return self.__line_plain(chain)

    def __line_colored(self, chain: PrefChain) -> str:
        sep = self.SEP
        end = self.END

        src, dst = self.__resolve(chain)
        color = self.__color_for(dst)

        if self._style == PrefListStyleOption.LONG:
            return sep.join([color.decorate(dst), str(src)]) + end

        if self._style == PrefListStyleOption.SHORT:
            return color.decorate(dst) + end

        return color.decorate(dst) + end

    def __line_plain(self, chain: PrefChain) -> str:
        sep = self.SEP
        end = self.END

        src, dst = self.__resolve(chain)

        if self._style == PrefListStyleOption.LONG:
            return sep.join([str(dst), str(src)]) + end

        if self._style == PrefListStyleOption.SHORT:
            return str(dst) + end

        return str(dst) + end

    def __colorful(self) -> bool:
        if self._color == PrefListColorOption.ALWAYS:
            return True

        if self._color == PrefListColorOption.NEVER:
            return False

        return self._stream.isatty()

    @staticmethod
    def __resolve(chain: PrefChain) -> tuple[Path, Path]:
        cwd = Path.cwd()

        return (
            chain.src.relative_to(cwd) if chain.src.is_relative_to(cwd) else chain.src,
            chain.dst if chain.dst.exists() else Path('(null)')
        )

    @staticmethod
    def __color_for(path: Path) -> Color:
        if not path.exists():
            return Color.RED

        if path.is_symlink():
            return Color.MAGENTA

        if path.is_dir():
            return Color.BLUE

        if path.is_file():
            return Color.RESET

        return Color.RESET


class PrefCleanupAction(PrefAction):
    _logger: Lumber
    _noop: bool

    def __init__(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        self._logger = logger
        self._noop = noop
        return

    def run(self):
        books = self._books(logger=self._logger, noop=self._noop)
        return self.perform(books)

    def perform(self, books: list[CookBook]):
        candidates: list[Path] = []

        for book in books:
            if book.private:
                continue

            candidates += [x.dst.expanduser() for x in book.recipes]

        found: list[Path] = []

        for path in sorted(candidates):
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
        self._logger.trace(f'rm -f {path}')

        if self._noop:
            return False

        path.unlink(missing_ok=True)
        return True
