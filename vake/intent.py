import glob
import itertools
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .kernel import Identity, Shell
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
    shell: Shell

    def __init__(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        self.logger = logger
        self.noop = noop
        self.shell = Shell(logger, noop)
        return

    @abstractmethod
    def run(self):
        pass


class Hook(metaclass=ABCMeta):
    @staticmethod
    def noop() -> 'Hook':
        return NoopHook()

    @abstractmethod
    def activate(self):
        pass

    @abstractmethod
    def deactivate(self):
        pass


class NoopHook(Hook):

    def activate(self):
        pass

    def deactivate(self):
        pass


# ==
# Pref
# ==
STATIC_DIR = "./static"
SNIPPET_DIR = "./snippet"


@dataclass
class Recipe:
    src: Path
    dst: Path
    hook: Hook = Hook.noop()

    @staticmethod
    def create(
        src: str,
        dst: str,
        hook: Hook = Hook.noop(),
    ) -> 'Recipe':
        return Recipe(src=Path(src), dst=Path(dst), hook=hook)

    @staticmethod
    def glob(
        src: str,
        dst: str,
        hook: Hook = Hook.noop(),
    ) -> List['Recipe']:
        pattern = str(Path(dst).expanduser())
        return [
            Recipe(src=Path(src), dst=Path(dst), hook=hook)
            for dst in glob.glob(pattern)
        ]


@dataclass
class Cookbook:
    recipes: List[Recipe]

    @staticmethod
    def bin() -> 'Cookbook':
        return Cookbook([
            Recipe.create(
                src="bin",
                dst="~/.bin"
            ),
        ])

    @staticmethod
    def sh() -> 'Cookbook':
        return Cookbook([
            Recipe.create(
                src="sh.d",
                dst="~/.sh.d"
            ),
        ])

    @staticmethod
    def bash() -> 'Cookbook':
        return Cookbook([
            Recipe.create(
                src="bash.d",
                dst="~/.bash.d"
            ),
            Recipe.create(
                src="bash_completion.d",
                dst="~/.bash_completion.d"
            ),
        ])

    @staticmethod
    def zsh() -> 'Cookbook':
        return Cookbook([
            Recipe.create(
                src="zsh.d",
                dst="~/.zsh.d"
            ),
            Recipe.create(
                src="zsh-completions",
                dst="~/.zsh-completions"
            ),
            Recipe.create(
                src="/usr/local/library/Contributions/brew_zsh_completion.zsh",
                dst="~/.zsh-completions/_brew"
            ),
        ])

    @staticmethod
    def git() -> 'Cookbook':
        return Cookbook([
            Recipe.create(
                src="gitconfig",
                dst="~/.gitconfig"
            ),
            Recipe.create(
                src="tigrc",
                dst="~/.tigrc"
            ),
        ])

    @staticmethod
    def vim(logger: Lumber = Lumber.noop(), noop: bool = False) -> 'Cookbook':
        return Cookbook([
            Recipe.create(
                src="vimrc",
                dst="~/.vimrc"
            ),
            Recipe.create(
                src="vim",
                dst="~/.vim",
                hook=VimHook(logger=logger, noop=noop)
            ),
        ])

    @staticmethod
    def asdf() -> 'Cookbook':
        return Cookbook([
            Recipe.create(
                src="asdfrc",
                dst="~/.asdfrc"
            ),
        ])

    @staticmethod
    def tmux() -> 'Cookbook':
        return Cookbook([
            Recipe.create(
                src="tmux.conf",
                dst="~/.tmux.conf"
            ),
        ])

    @staticmethod
    def gradle() -> 'Cookbook':
        return Cookbook([
            Recipe.create(
                src="gradle",
                dst="~/.gradle"
            ),
        ])

    @staticmethod
    def xcode() -> 'Cookbook':
        return Cookbook([
            *Recipe.glob(
                src="Xcode",
                dst="~/Library/Developer/Xcode"
            )
        ])

    @staticmethod
    def intellij_idea() -> 'Cookbook':
        return Cookbook([
            *Recipe.glob(
                src="IntelliJIdea",
                dst="~/Library/Preferences/IntelliJIdea*"
            ),
            *Recipe.glob(
                src="IntelliJIdea",
                dst="~/Library/ApplicationSupport/JetBrains/IntelliJIdea*"
            ),
        ])

    @staticmethod
    def android_studio() -> 'Cookbook':
        return Cookbook([
            *Recipe.glob(
                src="AndroidStudio",
                dst="~/Library/Preferences/AndroidStudio*"
            ),
            *Recipe.glob(
                src="AndroidStudio",
                dst="~/Library/ApplicationSupport/Google/AndroidStudio*"
            ),
        ])

    @staticmethod
    def app_code() -> 'Cookbook':
        return Cookbook([
            *Recipe.glob(
                src="AppCode",
                dst="~/Library/Preferences/AppCode*"
            ),
            *Recipe.glob(
                src="AppCode",
                dst="~/Library/ApplicationSupport/JetBrains/AppCode*"
            ),
        ])

    @staticmethod
    def ruby_mine() -> 'Cookbook':
        return Cookbook([
            *Recipe.glob(
                src="RubyMine",
                dst="~/Library/Preferences/RubyMine*"
            ),
            *Recipe.glob(
                src="RubyMine",
                dst="~/Library/ApplicationSupport/JetBrains/RubyMine*"
            ),
        ])

    @staticmethod
    def go_land() -> 'Cookbook':
        return Cookbook([
            *Recipe.glob(
                src="GoLand",
                dst="~/Library/Preferences/GoLand*"
            ),
            *Recipe.glob(
                src="GoLand",
                dst="~/Library/ApplicationSupport/JetBrains/GoLand*"
            ),
        ])

    @staticmethod
    def c_lion() -> 'Cookbook':
        return Cookbook([
            *Recipe.glob(
                src="CLion",
                dst="~/Library/Preferences/CLion*"
            ),
            *Recipe.glob(
                src="CLion",
                dst="~/Library/ApplicationSupport/JetBrains/CLion*"
            ),
        ])

    @staticmethod
    def rider() -> 'Cookbook':
        return Cookbook([
            *Recipe.glob(
                src="Rider",
                dst="~/Library/Preferences/Rider*"
            ),
            *Recipe.glob(
                src="Rider",
                dst="~/Library/ApplicationSupport/JetBrains/Rider*"
            ),
        ])


class PrefAction(Action, metaclass=ABCMeta):
    def recipes(self) -> List[Recipe]:
        books: List[Cookbook] = []
        identity = Identity.detect()

        # shared
        books += [
            Cookbook.bin(),
            Cookbook.sh(),
            Cookbook.bash(),
            Cookbook.zsh(),
            Cookbook.git(),
            Cookbook.vim(logger=self.logger, noop=self.noop),
            Cookbook.tmux(),
            Cookbook.gradle(),
        ]

        # linux
        if identity.is_linux():
            books += []

        # darwin
        if identity.is_darwin():
            books += [
                Cookbook.xcode(),
                Cookbook.intellij_idea(),
                Cookbook.android_studio(),
                Cookbook.app_code(),
                Cookbook.ruby_mine(),
                Cookbook.go_land(),
                Cookbook.c_lion(),
                Cookbook.rider(),
            ]

        return list(itertools.chain.from_iterable([book.recipes for book in books]))

    @staticmethod
    def snippets() -> List[Recipe]:
        return [
            # sh
            Recipe.create(
                src="shrc",
                dst="~/.shrc"
            ),

            # bash
            Recipe.create(
                src="bashrc",
                dst="~/.bashrc"
            ),
            Recipe.create(
                src="bash_profile",
                dst="~/.bash_profile"
            ),

            # zsh
            Recipe.create(
                src="zshrc",
                dst="~/.zshrc"
            ),
            Recipe.create(
                src="zshprofile",
                dst="~/.zshprofile"
            ),
        ]


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

    def __run(self, recipe: Recipe, identifier="default") -> bool:
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

            # ensure parent directory
            dst_dir = dst.parent
            if not dst_dir.is_dir():
                self.shell.mkdir(dst_dir, recursive=True)

            # create symbolic link
            return self.shell.symlink(src, dst, force=True)

        #
        # directory
        #
        if src.is_dir():
            for new_src in [x for x in src.glob("**/*") if x.is_file()]:
                new_dst = Path(recipe.dst, new_src.relative_to(src))
                new_recipe = Recipe(src=new_src, dst=new_dst)
                self.__run(new_recipe, identifier=identifier)

        return True

    def __enable(self, snippet: Recipe):

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
    def __istarget(recipe: Recipe):
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

    def __run(self, recipe: Recipe, identifier: str = "default") -> bool:
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
            return self.shell.remove(dst)

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
                new_recipe = Recipe(src=new_src, dst=new_dst)
                self.__run(new_recipe, identifier=identifier)

        return True

    def __disable(self, snippet: Recipe):

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
    def __istarget(recipe: Recipe):
        blacklist = ['*.swp', '*.DS_Store']

        for pattern in blacklist:
            if recipe.src.match(pattern):
                return False

        return True


class PrefStatusAction(PrefAction):
    def run(self):
        identity = Identity.detect()
        recipes = sorted(self.recipes(), key=lambda x: x.dst)

        for recipe in recipes:
            target = Path(recipe.dst).expanduser()

            if not target.exists():
                continue

            if identity.is_darwin():
                self.shell.execute(f"ls -lFG {target}")
            else:
                self.shell.execute(f"ls -lFo {target}")

        return True


class VimHook(Hook):
    logger: Lumber
    noop: bool
    shell: Shell

    def __init__(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        self.logger = logger
        self.noop = noop
        self.shell = Shell(logger, noop)
        return

    def activate(self):
        dst = Path("~/.vim/autoload/plug.vim").expanduser()

        if dst.is_file():
            self.logger.info(f"Vim-Plug is already downloaded: {dst}")
            return

        self.shell.execute([
            "curl",
            "--fail",
            "--location",
            "--create-dirs",
            "--output", str(dst),
            "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim"
        ])

    def deactivate(self):
        pass


# ==
# Brew
# ==
BREW = "brew"
BREWFILE = "Brewfile"


@dataclass(eq=True, frozen=True)
class Keg:
    name: str


class BrewAction(Action, metaclass=ABCMeta):
    def load_kegs(self) -> List[Keg]:
        identity = Identity.detect()
        src = Path(STATIC_DIR, identity.value, BREWFILE).resolve()

        self.logger.debug(f"Read kegs from file: {src}")

        if not src.exists():
            return []

        lines = src.read_text().splitlines()
        return [Keg(name) for name in lines]

    def list_kegs(self) -> List[Keg]:
        stdout = self.shell.capture([BREW, "list"]).stdout
        lines = stdout.decode('utf8').strip().splitlines()
        return [Keg(name) for name in lines]


class BrewInstallAction(BrewAction):
    def run(self):
        if not self.shell.available(BREW):
            self.logger.warning(f"Command is not available: {BREW}")
            return

        kegs = self.load_kegs()

        if not kegs:
            self.logger.info("No available kegs were found")
            return

        found = set(self.list_kegs())

        for keg in kegs:
            if keg in found:
                self.logger.info(f"{keg.name} is already installed")
            else:
                self.shell.execute([BREW, "install", keg.name])

        return


class BrewUninstallAction(BrewAction):
    def run(self):
        if not self.shell.available(BREW):
            self.logger.warn(f"Command is not available: {BREW}")
            return

        kegs = self.load_kegs()

        if not kegs:
            self.logger.info("No available kegs were found")
            return

        found = set(self.list_kegs())

        for keg in found:
            if keg in found:
                self.shell.execute([BREW, "uninstall", keg.name])
            else:
                self.logger.info(f"{keg.name} is not installed")

        return


class BrewStatusAction(BrewAction):
    def run(self):
        if not self.shell.available(BREW):
            self.logger.warn(f"Command is not available: {BREW}")
            return

        self.shell.execute([BREW, "tap"])
        self.shell.execute([BREW, "list"])
        return
