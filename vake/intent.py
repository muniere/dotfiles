import os
import re
import sys
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import TextIO, List, Tuple

from . import config
from . import kernel
from . import locate
from .box import TernaryBox
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
    def _books(reverse: bool = False) -> List[CookBook]:
        identity = kernel.identify()

        # shared
        core_books: List[CookBook] = [
            config.BinCookBook(),
            config.ShCookBook(),
            config.BashCookBook(),
            config.ZshCookBook(),
            config.VimCookBook(),
            config.GitCookBook(),
            config.GitHubCookBook(),
            config.AsdfCookBook(),
            config.TmuxCookBook(),
            config.RangerCookBook(),
            config.GradleCookBook(),
            config.RubyCookBook(),
            config.NodeCookBook(),
        ]

        pre_books: List[CookBook] = []
        post_books: List[CookBook] = []

        # linux
        if identity.is_linux():
            pre_books += []
            post_books += []

        # darwin
        if identity.is_darwin():
            pre_books += [
                config.BrewCookBook(),
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


@dataclass(frozen=True)
class PrefLinkAction(PrefAction):
    intents: List[str] = field(default_factory=lambda: [])
    logger: Lumber = field(default_factory=lambda: Lumber.noop())
    cleanup: bool = field(default_factory=lambda: True)
    activate: bool = field(default_factory=lambda: True)
    noop: bool = field(default_factory=lambda: False)

    def run(self):
        books = [it for it in self._books(reverse=False) if self.__test(it)]

        aliases = set().union(*[book.aliases for book in books])
        illegals = [it for it in self.intents if it not in aliases]
        if illegals:
            self.logger.warn(f'Intents not supported: {", ".join(illegals)}')

        if self.cleanup:
            PrefCleanupAction(logger=self.logger, noop=self.noop).perform(books)

        return self.perform(books)

    def perform(self, books: List[CookBook]):
        identity = kernel.identify()

        for i, book in enumerate(books, start=1):
            self.logger.mark(f"{book.name} Launched ({i:02}/{len(books):02})".ljust(80), bold=True)

            for recipe in book.recipes:
                if recipe.src.is_absolute():
                    chains = recipe.expand()
                else:
                    chains = recipe.expand(src_prefix=Path(locate.recipe(), identity.value)) + \
                             recipe.expand(src_prefix=Path(locate.recipe(), 'default'))

                for chain in chains:
                    self.__link(chain)

            for snippet in book.snippets:
                self.__enable(snippet)

            if self.activate:
                book.activate(logger=self.logger, noop=self.noop)

    def __test(self, book: CookBook) -> bool:
        if self.intents:
            return bool(book.aliases.intersection(self.intents))
        else:
            return True

    def __link(self, chain: PrefChain) -> bool:
        if not self._test(chain.src):
            self.logger.debug(f'File ignored: {chain.src}')
            return False

        if not chain.src.exists():
            self.logger.info(f'File not found: {chain.src}')
            return False

        if chain.dst.is_symlink():
            self.logger.info(f'Symlink already exists: {chain.dst}')
            return False

        if chain.dst.is_file():
            self.logger.info(f'File already exists: {chain.dst}')
            return False

        if not chain.dst.parent.is_dir():
            self.__mkdir(chain.dst.parent)

        self.__symlink(chain.src, chain.dst)
        return True

    def __mkdir(self, path: Path) -> bool:
        self.logger.trace(f'mkdir -p {path}')

        if self.noop:
            return False

        path.mkdir(parents=True, exist_ok=True)
        return True

    def __symlink(self, src: Path, dst: Path) -> bool:
        self.logger.trace(f'ln -s -f {src} {dst}')

        if self.noop:
            return False

        dst.symlink_to(src)
        return True

    def __enable(self, snippet: SnipRecipe) -> bool:
        src = Path(locate.snippet(), snippet.src).resolve()
        dst = Path(snippet.dst).expanduser()

        if not src.exists():
            self.logger.info(f'File not found: {snippet.src}')
            return False

        src_str = src.read_text(encoding='utf-8').strip()
        dst_str = dst.read_text(encoding='utf-8').strip() if dst.exists() else ''

        if src_str in dst_str:
            self.logger.info(f'Snippet already enabled: {dst}')
            return False

        self.logger.info(f'Enable snippet: {src}')

        if self.noop:
            return False

        new_str = TernaryBox(len(dst_str)).fold(
            some=lambda: dst_str + os.linesep + src_str + os.linesep,
            none=lambda: src_str + os.linesep,
        )

        dst.write_text(new_str, encoding='utf-8')
        return True


@dataclass(frozen=True)
class PrefUnlinkAction(PrefAction):
    intents: List[str] = field(default_factory=lambda: [])
    logger: Lumber = field(default_factory=lambda: Lumber.noop())
    cleanup: bool = field(default_factory=lambda: True)
    deactivate: bool = field(default_factory=lambda: True)
    noop: bool = field(default_factory=lambda: False)

    def run(self):
        books = [it for it in self._books(reverse=False) if self.__test(it)]

        aliases = set().union(*[book.aliases for book in books])
        illegals = [it for it in self.intents if it not in aliases]
        if illegals:
            self.logger.warn(f'Intents not supported: {", ".join(illegals)}')

        if self.cleanup:
            PrefCleanupAction(logger=self.logger, noop=self.noop).perform(books)

        return self.perform(books)

    def perform(self, books: List[CookBook]):
        identity = kernel.identify()

        for i, book in enumerate(books, start=1):
            self.logger.mark(f"{book.name} Launched ({i:02}/{len(books)})".ljust(80), bold=True)

            if self.deactivate:
                book.deactivate(logger=self.logger, noop=self.noop)

            for snippet in book.snippets:
                self.__disable(snippet)

            for recipe in book.recipes:
                if recipe.src.is_absolute():
                    chains = recipe.expand()
                else:
                    chains = recipe.expand(src_prefix=Path(locate.recipe(), identity.value)) + \
                             recipe.expand(src_prefix=Path(locate.recipe(), 'default'))

                for chain in chains:
                    self.__unlink(chain)

        return

    def __test(self, book: CookBook) -> bool:
        if self.intents:
            return bool(book.aliases.intersection(self.intents))
        else:
            return True

    def __unlink(self, chain: PrefChain) -> bool:
        if not self._test(chain.src):
            self.logger.debug(f'File is not target: {chain.src}')
            return False

        if not chain.src.exists():
            self.logger.info(f'File not found: {chain.src}')
            return False

        if not chain.dst.exists() and not chain.dst.is_symlink():
            self.logger.info(f'File already removed: {chain.dst}')
            return True

        return self.__rm(chain.dst)

    def __rm(self, path: Path) -> bool:
        self.logger.trace(f'rm -f {path}')

        if self.noop:
            return False

        path.unlink(missing_ok=True)
        return True

    def __disable(self, snippet: SnipRecipe) -> bool:
        src = Path(locate.snippet(), snippet.src).resolve()
        dst = Path(snippet.dst).expanduser()

        if not src.exists():
            self.logger.info(f'File not found: {src}')
            return False

        if not dst.exists():
            self.logger.info(f'File not found: {dst}')
            return False

        src_str = src.read_text(encoding='utf-8').strip()
        dst_str = dst.read_text(encoding='utf-8')

        if src_str not in dst_str:
            self.logger.info(f'Snippet already disabled: {dst}')
            return False

        self.logger.info(f'Disable snippet: {src}')

        if self.noop:
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


@dataclass(frozen=True)
class PrefListAction(PrefAction):
    stream: TextIO = field(default_factory=lambda: sys.stdout)
    color: PrefListColorOption = field(default_factory=lambda: PrefListColorOption.AUTO)
    style: PrefListStyleOption = field(default_factory=lambda: PrefListStyleOption.SHORT)

    SEP = ' -> '
    END = os.linesep

    def run(self):
        identity = kernel.identify()
        books = self._books()

        chains: List[PrefChain] = []

        for book in books:
            for recipe in book.recipes:
                if recipe.src.is_absolute():
                    chains += recipe.expand()
                else:
                    chains += recipe.expand(src_prefix=Path(locate.recipe(), identity.value))
                    chains += recipe.expand(src_prefix=Path(locate.recipe(), 'default'))

        chains.sort(key=lambda x: x.dst)
        lines = [self.__line(x) for x in chains if self._test(x.src)]

        self.stream.writelines(lines)
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

        if self.style == PrefListStyleOption.LONG:
            return sep.join([color.decorate(dst), str(src)]) + end

        if self.style == PrefListStyleOption.SHORT:
            return color.decorate(dst) + end

        return color.decorate(dst) + end

    def __line_plain(self, chain: PrefChain) -> str:
        sep = self.SEP
        end = self.END

        src, dst = self.__resolve(chain)

        if self.style == PrefListStyleOption.LONG:
            return sep.join([str(dst), str(src)]) + end

        if self.style == PrefListStyleOption.SHORT:
            return str(dst) + end

        return str(dst) + end

    def __colorful(self) -> bool:
        if self.color == PrefListColorOption.ALWAYS:
            return True

        if self.color == PrefListColorOption.NEVER:
            return False

        return self.stream.isatty()

    @staticmethod
    def __resolve(chain: PrefChain) -> Tuple[Path, Path]:
        cwd = Path.cwd()

        return (
            chain.resolve_src(cwd),
            chain.resolve_dst(),
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


@dataclass(frozen=True)
class PrefCleanupAction(PrefAction):
    intents: List[str] = field(default_factory=lambda: [])
    logger: Lumber = field(default_factory=lambda: Lumber.noop())
    noop: bool = field(default_factory=lambda: False)

    def run(self):
        books = [it for it in self._books(reverse=False) if self.__test(it)]

        aliases = set().union(*[book.aliases for book in books])
        illegals = [it for it in self.intents if it not in aliases]
        if illegals:
            self.logger.warn(f'Intents not supported: {", ".join(illegals)}')

        return self.perform(books)

    def perform(self, books: List[CookBook]):
        candidates: List[Path] = []

        for book in books:
            if book.private:
                continue

            candidates += [x.dst.expanduser() for x in book.recipes]

        found: List[Path] = []

        for path in sorted(candidates):
            message = f'Scanning {path}'
            self.logger.debug(f'{message}...\r', terminate=False)
            found += self.__scan(path)
            self.logger.debug(f'{message}... Done')

        self.logger.debug(f'Found {len(found)} broken symlinks')
        for path in found:
            self.__rm(path)

        return

    def __test(self, book: CookBook) -> bool:
        if self.intents:
            return bool(book.aliases.intersection(self.intents))
        else:
            return True

    @staticmethod
    def __scan(path: Path) -> List[Path]:
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
        self.logger.trace(f'rm -f {path}')

        if self.noop:
            return False

        path.unlink(missing_ok=True)
        return True
