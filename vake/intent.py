import itertools
import os
import re
from abc import ABCMeta, abstractmethod
from pathlib import Path

from . import brew
from . import config
from . import kernel
from . import locate
from . import shell
from .config import PrefChain, PrefRecipe, PrefBook, SnipRecipe, SnipBook
from .timber import Lumber

__all__ = [
    'Action',
    'PrefInstallAction', 'PrefUninstallAction', 'PrefStatusAction',
    'BrewInstallAction', 'BrewUninstallAction', 'BrewStatusAction',
]


# ==
# Base
# ==
class Action(metaclass=ABCMeta):
    _logger: Lumber
    _noop: bool

    def __init__(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        self._logger = logger
        self._noop = noop
        return

    @abstractmethod
    def run(self):
        pass


# ==
# Pref
# ==
class PrefAction(Action, metaclass=ABCMeta):
    def _recipes(self) -> list[PrefRecipe]:
        identity = kernel.identify()

        # shared
        books: list[PrefBook] = [
            config.BinPrefBook(),
            config.ShPrefBook(),
            config.BashPrefBook(),
            config.ZshPrefBook(logger=self._logger, noop=self._noop),
            config.GitPrefBook(),
            config.VimPrefBook(logger=self._logger, noop=self._noop),
            config.TmuxPrefBook(),
            config.GradlePrefBook(),
        ]

        # linux
        if identity.is_linux():
            books += []

        # darwin
        if identity.is_darwin():
            books += [
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


class PrefInstallAction(PrefAction):
    def run(self):
        identity = kernel.identify()

        for recipe in self._recipes():
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

        return

    def __link(self, chain: PrefChain) -> bool:
        if not self._test(chain.src):
            self._logger.info(f'File is not target: {chain.src}')
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


class PrefUninstallAction(PrefAction):
    def run(self):
        identity = kernel.identify()

        for recipe in self._recipes():
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
            self._logger.info(f'File is not target: {chain.src}')
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


class PrefStatusAction(PrefAction):
    def run(self):
        identity = kernel.identify()
        recipes = sorted(self._recipes(), key=lambda x: x.dst)

        for recipe in recipes:
            dst = Path(recipe.dst).expanduser()

            if not dst.exists():
                continue

            if identity.is_darwin():
                shell.call(['ls', '-lFG', str(dst)], logger=self._logger, noop=False)
            else:
                shell.call(['ls', '-lFo', str(dst)], logger=self._logger, noop=False)

        return True


# ==
# Brew
# ==
class BrewAction(Action, metaclass=ABCMeta):
    pass


class BrewInstallAction(BrewAction):
    def run(self):
        try:
            brew.ensure()
        except AssertionError as err:
            self._logger.error(err)
            return

        kegs = brew.load_list()

        if len(kegs) == 0:
            self._logger.info('No available kegs were found')
            return

        found = brew.run_list()

        for keg in kegs:
            if keg in found:
                self._logger.info(f'{keg.name} is already installed')
            else:
                brew.call_install(keg, logger=self._logger, noop=self._noop)

        return


class BrewUninstallAction(BrewAction):
    def run(self):
        try:
            brew.ensure()
        except AssertionError as err:
            self._logger.error(err)
            return

        kegs = brew.load_list()

        if len(kegs) == 0:
            self._logger.info('No available kegs were found')
            return

        found = brew.run_list()

        for keg in found:
            if keg in found:
                brew.call_uninstall(keg, logger=self._logger, noop=self._noop)
            else:
                self._logger.info(f'{keg.name} is not installed')

        return


class BrewStatusAction(BrewAction):
    def run(self):
        try:
            brew.ensure()
        except AssertionError as err:
            self._logger.error(err)
            return

        brew.call_tap(logger=self._logger, noop=False)
        brew.call_list(logger=self._logger, noop=False)
        return
