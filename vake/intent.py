import itertools
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List

from . import provision
from .kernel import Identity, Shell
from .provision import PrefRecipe, PrefBook, SnipRecipe, SnipBook
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
STATIC_DIR = "./static"
SNIPPET_DIR = "./snippet"


class PrefAction(Action, metaclass=ABCMeta):
    def recipes(self) -> List[PrefRecipe]:
        identity = Identity.detect()

        # shared
        books: List[PrefBook] = [
            provision.BinPrefBook(),
            provision.ShPrefBook(),
            provision.BashPrefBook(),
            provision.ZshPrefBook(),
            provision.GitPrefBook(),
            provision.VimPrefBook(logger=self.logger, noop=self.noop),
            provision.TmuxPrefBook(),
            provision.GradlePrefBook(),
        ]

        # linux
        if identity.is_linux():
            books += []

        # darwin
        if identity.is_darwin():
            books += [
                provision.XcodePrefBook(),
                provision.IntelliJIdeaPrefBook(),
                provision.AndroidStudioPrefBook(),
                provision.AppCodePrefBook(),
                provision.RubyMinePrefBook(),
                provision.GoLandPrefBook(),
                provision.CLionPrefBook(),
                provision.RiderPrefBook(),
            ]

        return list(itertools.chain(*[book.recipes for book in books]))

    @staticmethod
    def snippets() -> List[SnipRecipe]:
        books: List[SnipBook] = [
            provision.ShSnipBook(),
            provision.BashSnipBook(),
            provision.ZshSnipBook(),
        ]

        return list(itertools.chain(*[book.recipes for book in books]))


class PrefInstallAction(PrefAction):
    def run(self):
        identity = Identity.detect()

        for recipe in self.recipes():
            if recipe.src.is_absolute():
                self.__run(recipe)
            else:
                self.__run(recipe, identifier=identity.value)
                self.__run(recipe, identifier="default")

            recipe.hook.activate()

        for snippet in self.snippets():
            self.__enable(snippet)

        return

    def __run(self, recipe: PrefRecipe, identifier="default") -> bool:
        if not self.__istarget(recipe):
            rel = Path(STATIC_DIR, identifier, recipe.src).relative_to(Path.cwd())
            self.logger.info(f"File is not target: {rel}")
            return False

        if recipe.src.is_absolute():
            src = Path(recipe.src)
        else:
            src = Path(STATIC_DIR, identifier, recipe.src).resolve()

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
            self.logger.info(f"Symlink already exists: {dst}")
            return False

        #
        # file
        #
        if src.is_file():
            # another file already exists
            if dst.is_file():
                self.logger.info(f"File already exists: {dst}")
                return False

            shell = Shell(logger=self.logger, noop=self.noop)

            # ensure parent directory
            dst_dir = dst.parent
            if not dst_dir.is_dir():
                shell.mkdir(dst_dir, recursive=True)

            # create symbolic link
            return shell.symlink(src, dst, force=True)

        #
        # directory
        #
        if src.is_dir():
            for new_src in [x for x in src.glob("**/*") if x.is_file()]:
                new_dst = Path(recipe.dst, new_src.relative_to(src))
                new_recipe = PrefRecipe(src=new_src, dst=new_dst)
                self.__run(new_recipe, identifier=identifier)

        return True

    def __enable(self, snippet: SnipRecipe):

        #
        # source
        #
        src = Path(SNIPPET_DIR, snippet.src)

        if not src.exists():
            return

        src_str = src.read_text().strip()

        #
        # destination
        #
        dst = Path(snippet.dst).expanduser()

        # new file
        if not dst.exists():
            self.logger.execute(f"Enable snippet {src}")

            if not self.noop:
                dst.write_text(src_str + "\n")

            return

        dst_str = dst.read_text()

        # skip: already enabled
        if src_str in dst_str:
            self.logger.info(f"Snippet already enabled: {dst}")
            return

        # enable
        self.logger.execute(f"Enable {src}")

        if not self.noop:
            dst.write_text(dst_str + src_str + "\n")

        return

    @staticmethod
    def __istarget(recipe: PrefRecipe):
        blacklist = ['*.swp', '*.bak', '*.DS_Store']

        for pattern in blacklist:
            if recipe.src.match(pattern):
                return False

        return True


class PrefUninstallAction(PrefAction):
    def run(self):
        identity = Identity.detect()

        for recipe in self.recipes():
            self.__run(recipe, identifier=identity.value)
            self.__run(recipe, identifier="default")

            recipe.hook.deactivate()

        for snippet in self.snippets():
            self.__disable(snippet)

        return

    def __run(self, recipe: PrefRecipe, identifier: str = "default") -> bool:
        if not self.__istarget(recipe):
            rel = Path(STATIC_DIR, identifier, recipe.src).relative_to(Path.cwd())
            self.logger.info(f"File is not target: {rel}")
            return False

        if recipe.src.is_absolute():
            src = Path(recipe.src)
        else:
            src = Path(STATIC_DIR, identifier, recipe.src).resolve()

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
            self.logger.info(f"File already removed: {dst}")
            return True

        #
        # symlink
        #
        if dst.is_symlink():
            shell = Shell(logger=self.logger, noop=self.noop)
            return shell.remove(dst)

        #
        # file
        #
        if dst.is_file():
            self.logger.info(f"File is not symlink: {dst}")
            return False

        #
        # directory
        #
        if src.is_dir():
            for new_src in [x for x in src.glob("**/*") if x.is_file()]:
                new_dst = Path(recipe.dst, new_src.relative_to(src))
                new_recipe = PrefRecipe(src=new_src, dst=new_dst)
                self.__run(new_recipe, identifier=identifier)

        return True

    def __disable(self, snippet: SnipRecipe):

        #
        # source
        #
        src = Path(SNIPPET_DIR, snippet.src)

        if not src.exists():
            return

        src_str = src.read_text().strip()

        #
        # destination
        #
        dst = Path(snippet.dst).expanduser()

        # not found
        if not dst.exists():
            self.logger.info(f"File NOT FOUND: {dst}")
            return

        dst_str = dst.read_text()

        # skip: already disabled
        if src_str not in dst_str:
            self.logger.info(f"Snippet already disabled: {dst}")
            return

        # disable
        self.logger.execute(f"Disable snippet {src}")

        if not self.noop:
            dst.write_text(dst_str.replace(src_str, ""))

        return

    @staticmethod
    def __istarget(recipe: PrefRecipe):
        blacklist = ['*.swp', '*.DS_Store']

        for pattern in blacklist:
            if recipe.src.match(pattern):
                return False

        return True


class PrefStatusAction(PrefAction):
    def run(self):
        identity = Identity.detect()
        recipes = sorted(self.recipes(), key=lambda x: x.dst)
        shell = Shell(logger=self.logger, noop=False)

        for recipe in recipes:
            target = Path(recipe.dst).expanduser()

            if not target.exists():
                continue

            if identity.is_darwin():
                shell.execute(f"ls -lFG {target}")
            else:
                shell.execute(f"ls -lFo {target}")

        return True


# ==
# Brew
# ==
BREW = "brew"
BREWFILE = "Brewfile"


@dataclass(frozen=True)
class Keg:
    name: str


class BrewAction(Action, metaclass=ABCMeta):
    def _validate(self):
        shell = Shell(logger=self.logger, noop=False)
        if not shell.available(BREW):
            raise RuntimeError(f'Command is not available: {BREW}')

    def _load_kegs(self) -> List[Keg]:
        identity = Identity.detect()
        src = Path(STATIC_DIR, identity.value, BREWFILE).resolve()

        self.logger.debug(f"Read kegs from file: {src}")

        if not src.exists():
            return []

        lines = src.read_text().splitlines()
        return [Keg(name) for name in lines]

    def _list_kegs(self) -> List[Keg]:
        shell = Shell(logger=self.logger, noop=False)
        stdout = shell.capture([BREW, "list"]).stdout
        lines = stdout.decode('utf8').strip().splitlines()
        return [Keg(name) for name in lines]


class BrewInstallAction(BrewAction):
    def run(self):
        try:
            self._validate()
        except Exception as err:
            self.logger.warning(err)
            return

        kegs = self._load_kegs()

        if not kegs:
            self.logger.info("No available kegs were found")
            return

        found = self._list_kegs()
        shell = Shell(logger=self.logger, noop=self.noop)

        for keg in kegs:
            if keg in found:
                self.logger.info(f"{keg.name} is already installed")
            else:
                shell.execute([BREW, "install", keg.name])

        return


class BrewUninstallAction(BrewAction):
    def run(self):
        try:
            self._validate()
        except Exception as err:
            self.logger.warning(err)
            return

        kegs = self._load_kegs()

        if not kegs:
            self.logger.info("No available kegs were found")
            return

        found = set(self._list_kegs())
        shell = Shell(logger=self.logger, noop=self.noop)

        for keg in found:
            if keg in found:
                shell.execute([BREW, "uninstall", keg.name])
            else:
                self.logger.info(f"{keg.name} is not installed")

        return


class BrewStatusAction(BrewAction):
    def run(self):
        try:
            self._validate()
        except Exception as err:
            self.logger.warning(err)
            return

        shell = Shell(logger=self.logger, noop=False)
        shell.execute([BREW, "tap"])
        shell.execute([BREW, "list"])
        return
