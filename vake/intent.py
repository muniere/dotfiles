import itertools
from abc import ABCMeta, abstractmethod
from pathlib import Path

from . import brew
from . import config
from . import kernel
from . import locate
from . import shell
from .config import PrefRecipe, PrefBook, SnipRecipe, SnipBook
from .timber import Lumber

__all__ = [
    'PrefInstallAction', 'PrefUninstallAction', 'PrefStatusAction',
    'BrewInstallAction', 'BrewUninstallAction', 'BrewStatusAction',
]


# ==
# Base
# ==
class Action(metaclass=ABCMeta):
    logger: Lumber
    noop: bool

    def __init__(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        self.logger = logger
        self.noop = noop
        return

    @abstractmethod
    def run(self):
        pass


# ==
# Pref
# ==
class PrefAction(Action, metaclass=ABCMeta):
    def recipes(self) -> list[PrefRecipe]:
        identity = kernel.identify()

        # shared
        books: list[PrefBook] = [
            config.BinPrefBook(),
            config.ShPrefBook(),
            config.BashPrefBook(),
            config.ZshPrefBook(),
            config.GitPrefBook(),
            config.VimPrefBook(logger=self.logger, noop=self.noop),
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
    def snippets() -> list[SnipRecipe]:
        books: list[SnipBook] = [
            config.ShSnipBook(),
            config.BashSnipBook(),
            config.ZshSnipBook(),
        ]

        return list(itertools.chain(*[book.recipes for book in books]))


class PrefInstallAction(PrefAction):
    def run(self):
        identity = kernel.identify()

        for recipe in self.recipes():
            if recipe.src.is_absolute():
                self.__run(recipe)
            else:
                self.__run(recipe, identifier=identity.value)
                self.__run(recipe, identifier='default')

            recipe.hook.activate()

        for snippet in self.snippets():
            self.__enable(snippet)

        return

    def __run(self, recipe: PrefRecipe, identifier='default') -> bool:
        if not self.__test(recipe):
            rel = Path(locate.static(), identifier, recipe.src).relative_to(Path.cwd())
            self.logger.info(f'File is not target: {rel}')
            return False

        if recipe.src.is_absolute():
            src = Path(recipe.src)
        else:
            src = Path(locate.static(), identifier, recipe.src).resolve()

        if recipe.dst.is_absolute():
            dst = Path(recipe.dst)
        else:
            dst = Path(recipe.dst).expanduser()

        #
        # guard
        #

        # src not found
        if not src.exists():
            return False

        # dst link already exists
        if dst.is_symlink():
            self.logger.info(f'Symlink already exists: {dst}')
            return False

        #
        # file
        #
        if src.is_file():
            # another file already exists
            if dst.is_file():
                self.logger.info(f'File already exists: {dst}')
                return False

            # ensure parent directory
            dst_dir = dst.parent
            if not dst_dir.is_dir():
                self.__mkdir(dst_dir)

            # create symbolic link
            return self.__symlink(src, dst)

        #
        # directory
        #
        if src.is_dir():
            for new_src in [x for x in src.glob('**/*') if x.is_file()]:
                new_dst = Path(recipe.dst, new_src.relative_to(src))
                new_recipe = PrefRecipe(src=new_src, dst=new_dst)
                self.__run(new_recipe, identifier=identifier)

        return True

    def __mkdir(self, path: Path) -> bool:
        self.logger.execute(f'mkdir -p {path}')

        if self.noop:
            return False

        path.mkdir(parents=True, exist_ok=True)
        return True

    def __symlink(self, src: Path, dst: Path) -> bool:
        self.logger.execute(f'ln -s -f {src} {dst}')

        if self.noop:
            return False

        dst.symlink_to(src)
        return True

    def __enable(self, snippet: SnipRecipe):

        #
        # source
        #
        src = Path(locate.snippet(), snippet.src)

        if not src.exists():
            return

        src_str = src.read_text(encoding='utf-8').strip()

        #
        # destination
        #
        dst = Path(snippet.dst).expanduser()

        # new file
        if not dst.exists():
            self.logger.execute(f'Enable snippet {src}')

            if self.noop:
                return

            dst.write_text(src_str + '\n', encoding='utf-8')
            return

        dst_str = dst.read_text(encoding='utf-8')

        # skip: already enabled
        if src_str in dst_str:
            self.logger.info(f'Snippet already enabled: {dst}')
            return

        # enable
        self.logger.execute(f'Enable {src}')

        if self.noop:
            return

        dst.write_text(dst_str + src_str + '\n', encoding='utf-8')
        return

    @staticmethod
    def __test(recipe: PrefRecipe):
        blacklist = ['*.swp', '*.bak', '*.DS_Store']

        for pattern in blacklist:
            if recipe.src.match(pattern):
                return False

        return True


class PrefUninstallAction(PrefAction):
    def run(self):
        identity = kernel.identify()

        for recipe in self.recipes():
            self.__run(recipe, identifier=identity.value)
            self.__run(recipe, identifier='default')

            recipe.hook.deactivate()

        for snippet in self.snippets():
            self.__disable(snippet)

        return

    def __run(self, recipe: PrefRecipe, identifier: str = 'default') -> bool:
        if not self.__test(recipe):
            rel = Path(locate.static(), identifier, recipe.src).relative_to(Path.cwd())
            self.logger.info(f'File is not target: {rel}')
            return False

        if recipe.src.is_absolute():
            src = Path(recipe.src)
        else:
            src = Path(locate.static(), identifier, recipe.src).resolve()

        if recipe.dst.is_absolute():
            dst = Path(recipe.dst)
        else:
            dst = Path(recipe.dst).expanduser()

        #
        # guard
        #

        # src not found
        if not src.exists():
            return True

        # dst not found
        if not dst.exists() and not dst.is_symlink():
            self.logger.info(f'File already removed: {dst}')
            return True

        #
        # symlink
        #
        if dst.is_symlink():
            return self.__rm(dst)

        #
        # file
        #
        if dst.is_file():
            self.logger.info(f'File is not symlink: {dst}')
            return False

        #
        # directory
        #
        if src.is_dir():
            for new_src in [x for x in src.glob('**/*') if x.is_file()]:
                new_dst = Path(recipe.dst, new_src.relative_to(src))
                new_recipe = PrefRecipe(src=new_src, dst=new_dst)
                self.__run(new_recipe, identifier=identifier)

        return True

    def __rm(self, path: Path) -> bool:
        self.logger.execute(f'rm -r -f {path}')

        if self.noop:
            return False

        path.unlink(missing_ok=True)
        return True

    def __disable(self, snippet: SnipRecipe):

        #
        # source
        #
        src = Path(locate.snippet(), snippet.src)

        if not src.exists():
            return

        src_str = src.read_text(encoding='utf-8').strip()

        #
        # destination
        #
        dst = Path(snippet.dst).expanduser()

        # not found
        if not dst.exists():
            self.logger.info(f'File NOT FOUND: {dst}')
            return

        dst_str = dst.read_text(encoding='utf-8')

        # skip: already disabled
        if src_str not in dst_str:
            self.logger.info(f'Snippet already disabled: {dst}')
            return

        # disable
        self.logger.execute(f'Disable snippet {src}')

        if self.noop:
            return

        dst.write_text(dst_str.replace(src_str, ''), encoding='utf-8')
        return

    @staticmethod
    def __test(recipe: PrefRecipe):
        blacklist = ['*.swp', '*.DS_Store']

        for pattern in blacklist:
            if recipe.src.match(pattern):
                return False

        return True


class PrefStatusAction(PrefAction):
    def run(self):
        identity = kernel.identify()
        recipes = sorted(self.recipes(), key=lambda x: x.dst)

        for recipe in recipes:
            dst = Path(recipe.dst).expanduser()

            if not dst.exists():
                continue

            if identity.is_darwin():
                shell.execute(['ls', '-lFG', str(dst)], logger=self.logger, noop=False)
            else:
                shell.execute(['ls', '-lFo', str(dst)], logger=self.logger, noop=False)

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
            self.logger.warning(err)
            return

        kegs = brew.load()

        if len(kegs) == 0:
            self.logger.info('No available kegs were found')
            return

        found = brew.capture()

        for keg in kegs:
            if keg in found:
                self.logger.info(f'{keg.name} is already installed')
            else:
                brew.install(keg, logger=self.logger, noop=self.noop)

        return


class BrewUninstallAction(BrewAction):
    def run(self):
        try:
            brew.ensure()
        except AssertionError as err:
            self.logger.warning(err)
            return

        kegs = brew.load()

        if len(kegs) == 0:
            self.logger.info('No available kegs were found')
            return

        found = brew.capture()

        for keg in found:
            if keg in found:
                brew.uninstall(keg, logger=self.logger, noop=self.noop)
            else:
                self.logger.info(f'{keg.name} is not installed')

        return


class BrewStatusAction(BrewAction):
    def run(self):
        try:
            brew.ensure()
        except AssertionError as err:
            self.logger.warning(err)
            return

        brew.tap(logger=self.logger, noop=False)
        brew.list(logger=self.logger, noop=False)
        return
