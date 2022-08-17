import os
import re
import sys
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TextIO, List

from . import config
from . import flow
from . import kernel
from . import locate
from .config import PrefChain, CookBook, SnipChain
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
            config.PythonCookBook(),
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
    def _blacklist(path: Path):
        blacklist = ['*.swp', '*.bak', '.DS_Store', '.keep', '.gitkeep']

        for pattern in blacklist:
            if path.match(pattern):
                return True

        return False


@dataclass(frozen=True)
class PrefLinkAction(PrefAction):
    intents: List[str] = field(default_factory=lambda: [])
    logger: Lumber = field(default_factory=lambda: Lumber.noop())
    cleanup: bool = field(default_factory=lambda: True)
    activate: bool = field(default_factory=lambda: True)
    noop: bool = field(default_factory=lambda: False)

    def run(self):
        books = [it for it in self._books(reverse=False) if self.__contains(it)]

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

            for pref in book.prefs:
                if pref.src.is_absolute():
                    pref_chains = pref.expand()
                else:
                    pref_chains = pref.expand(src_prefix=Path(locate.recipe(), identity.value)) + \
                                  pref.expand(src_prefix=Path(locate.recipe(), 'default'))

                for chain in pref_chains:
                    self.__link(chain)

            for snip in book.snips:
                if snip.src.is_absolute():
                    snip_chains = snip.expand()
                else:
                    snip_chains = snip.expand(src_prefix=Path(locate.snippet()))

                for chain in snip_chains:
                    self.__enable(chain)

            if self.activate:
                book.activate(logger=self.logger, noop=self.noop)

    def __contains(self, book: CookBook) -> bool:
        if self.intents:
            return bool(book.aliases.intersection(self.intents))
        else:
            return True

    def __link(self, chain: PrefChain) -> bool:
        if self._blacklist(chain.src):
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

    def __enable(self, chain: SnipChain) -> bool:
        if self._blacklist(chain.src):
            self.logger.debug(f'File ignored: {chain.src}')
            return False

        if not chain.src.exists():
            self.logger.info(f'File not found: {chain.src}')
            return False

        src_str = chain.src.read_text(encoding='utf-8').strip()
        dst_str = chain.dst.read_text(encoding='utf-8').strip() if chain.dst.exists() else ''

        if src_str in dst_str:
            self.logger.info(f'Snippet already enabled in file: {chain.dst}')
            return False

        self.logger.info(f'Enable snippet: {chain.src} >> {chain.dst}')

        if self.noop:
            return False

        new_str = flow.branch(
            value=dst_str,
            truthy=lambda: dst_str + os.linesep + src_str + os.linesep,
            falsy=lambda: src_str + os.linesep,
        )

        chain.dst.write_text(new_str, encoding='utf-8')
        return True


@dataclass(frozen=True)
class PrefUnlinkAction(PrefAction):
    intents: List[str] = field(default_factory=lambda: [])
    logger: Lumber = field(default_factory=lambda: Lumber.noop())
    cleanup: bool = field(default_factory=lambda: True)
    deactivate: bool = field(default_factory=lambda: True)
    noop: bool = field(default_factory=lambda: False)

    def run(self):
        books = [it for it in self._books(reverse=True) if self.__contains(it)]

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

            for snip in book.snips:
                if snip.src.is_absolute():
                    snip_chains = snip.expand()
                else:
                    snip_chains = snip.expand(src_prefix=Path(locate.snippet()))

                for chain in snip_chains:
                    self.__disable(chain)

            for pref in book.prefs:
                if pref.src.is_absolute():
                    pref_chains = pref.expand()
                else:
                    pref_chains = pref.expand(src_prefix=Path(locate.recipe(), identity.value)) + \
                                  pref.expand(src_prefix=Path(locate.recipe(), 'default'))

                for chain in pref_chains:
                    self.__unlink(chain)

        return

    def __contains(self, book: CookBook) -> bool:
        if self.intents:
            return bool(book.aliases.intersection(self.intents))
        else:
            return True

    def __unlink(self, chain: PrefChain) -> bool:
        if self._blacklist(chain.src):
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

    def __disable(self, chain: SnipChain) -> bool:
        if self._blacklist(chain.src):
            self.logger.debug(f'File is not target: {chain.src}')
            return False

        if not chain.src.exists():
            self.logger.info(f'File not found: {chain.src}')
            return False

        if not chain.dst.exists():
            self.logger.info(f'File not found: {chain.dst}')
            return False

        src_str = chain.src.read_text(encoding='utf-8').strip()
        dst_str = chain.dst.read_text(encoding='utf-8')

        if src_str not in dst_str:
            self.logger.info(f'Snippet already disabled in file: {chain.dst}')
            return False

        self.logger.info(f'Disable snippet: {chain.src} << {chain.dst}')

        if self.noop:
            return False

        pattern = re.escape(src_str) + os.linesep + '*'
        new_str = re.sub(pattern, '', dst_str)
        chain.dst.write_text(new_str, encoding='utf-8')
        return True


class PrefListColorOption(Enum):
    AUTO = 'auto'
    ALWAYS = 'always'
    NEVER = 'never'


class PrefListStyleOption(Enum):
    SHORT = 'short'
    LONG = 'long'


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
            for pref in book.prefs:
                if pref.src.is_absolute():
                    chains += pref.expand()
                else:
                    chains += pref.expand(src_prefix=Path(locate.recipe(), identity.value))
                    chains += pref.expand(src_prefix=Path(locate.recipe(), 'default'))

        chains.sort(key=lambda x: x.dst)
        lines = [self.__format(x) for x in chains if not self._blacklist(x.src)]

        self.stream.writelines(lines)
        return

    def __format(self, chain: PrefChain) -> str:
        sep = self.SEP
        end = self.END
        cwd = Path.cwd()

        src = chain.resolve_src(cwd)
        dst = chain.resolve_dst()

        if self.__colorful():
            color = self.__color_for(dst)

            if self.style == PrefListStyleOption.LONG:
                return sep.join([color.decorate(dst), str(src)]) + end

            if self.style == PrefListStyleOption.SHORT:
                return color.decorate(dst) + end

            return color.decorate(dst) + end

        else:
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
        books = [it for it in self._books(reverse=False) if self.__contains(it)]

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

            candidates += [x.dst.expanduser() for x in book.prefs]

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

    def __contains(self, book: CookBook) -> bool:
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
