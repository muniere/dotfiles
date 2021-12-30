import glob
import itertools
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

from .kernel import Identity, Shell
from .winston import LoggerWrapper

__all__ = [
    'PrefInstallAction', 'PrefUninstallAction', 'PrefStatusAction',
    'BrewInstallAction', 'BrewUninstallAction', 'BrewStatusAction',
]


# ==
# Base
# ==
class Action(metaclass=ABCMeta):
    noop: bool
    logger: Optional[LoggerWrapper]
    shell: Shell

    def __init__(self, noop: bool = False, logger: Optional[LoggerWrapper] = None):
        self.noop = noop
        self.logger = logger
        self.shell = Shell(noop, logger)
        return

    @abstractmethod
    def run(self):
        pass


class Hook(metaclass=ABCMeta):
    noop: bool
    logger: Optional[LoggerWrapper]
    shell: Shell

    def __init__(self, noop: bool = False, logger: Optional[LoggerWrapper] = None):
        self.noop = noop
        self.logger = logger
        self.shell = Shell(noop, logger)
        return

    @abstractmethod
    def activate(self):
        pass

    @abstractmethod
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
    hook: Optional[Hook] = None

    @staticmethod
    def create(
        src: str,
        dst: str,
        hook: Optional[Hook] = None,
    ) -> 'Recipe':
        return Recipe(src=Path(src), dst=Path(dst), hook=hook)

    @staticmethod
    def glob(
        src: str,
        dst: str,
        hook: Optional[Hook] = None,
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
    def vim(noop: bool = False, logger: Optional[LoggerWrapper] = None) -> 'Cookbook':
        return Cookbook([
            Recipe.create(
                src="vimrc",
                dst="~/.vimrc"
            ),
            Recipe.create(
                src="vim",
                dst="~/.vim",
                hook=VimHook(noop=noop, logger=logger)
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
            Cookbook.vim(noop=self.noop, logger=self.logger),
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

            if recipe.hook:
                recipe.hook.activate()

        for snippet in self.snippets():
            self.__enable(snippet)

        return

    def __run(self, recipe: Recipe, identifier="default") -> bool:
        if not self.__istarget(recipe):
            if self.logger:
                rel = Path(STATIC_DIR, identifier, recipe.src).relative_to(Path.cwd())
                self.logger.info("File is not target: %s" % rel)
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
            if self.logger:
                self.logger.info("Symlink already exists: %s" % dst)
            return False

        #
        # file
        #
        if src.is_file():
            # another file already exists
            if dst.is_file():
                if self.logger:
                    self.logger.info("File already exists: %s" % dst)
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
            if self.logger:
                self.logger.execute("Enable snippet %s" % src)

            if not self.noop:
                dst.write_text(src_str + "\n")

            return

        dst_str = dst.read_text()

        # skip: already enabled
        if src_str in dst_str:
            if self.logger:
                self.logger.info("Snippet already enabled: %s" % dst)
            return

        # enable
        if self.logger:
            self.logger.execute("Enable %s" % src)

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

            if recipe.hook:
                recipe.hook.deactivate()

        for snippet in self.snippets():
            self.__disable(snippet)

        return

    def __run(self, recipe: Recipe, identifier: str = "default") -> bool:
        if not self.__istarget(recipe):
            if self.logger:
                rel = Path(STATIC_DIR, identifier, recipe.src).relative_to(Path.cwd())
                self.logger.info("File is not target: %s" % rel)
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
            if self.logger:
                self.logger.info("File already removed: %s" % dst)
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
            if self.logger:
                self.logger.info("File is not symlink: %s" % dst)
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
            self.logger.info("File NOT FOUND: %s" % dst)
            return

        dst_str = dst.read_text()

        # skip: already disabled
        if src_str not in dst_str:
            if self.logger:
                self.logger.info("Snippet already disabled: %s" % dst)
            return

        # disable
        if self.logger:
            self.logger.execute("Disable snippet %s" % src)

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
                self.shell.execute("ls -lFG %s" % target)
            else:
                self.shell.execute("ls -lFo %s" % target)

        return True


class VimHook(Hook):

    def activate(self):
        dst = Path("~/.vim/autoload/plug.vim").expanduser()

        if dst.is_file():
            self.logger.info("Vim-Plug is already downloaded: %s" % dst)
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

        if self.logger:
            self.logger.debug("Read kegs from file: %s" % src)

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
            self.logger.warning("Command is not available: %s" % BREW)
            return

        kegs = self.load_kegs()

        if not kegs:
            self.logger.info("No available kegs were found")
            return

        found = set(self.list_kegs())

        for keg in kegs:
            if keg in found:
                self.logger.info("%s is already installed" % keg.name)
            else:
                self.shell.execute([BREW, "install", keg.name])

        return


class BrewUninstallAction(BrewAction):
    def run(self):
        if not self.shell.available(BREW):
            self.logger.warn("Command is not available: %s" % BREW)
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
                self.logger.info("%s is not installed" % keg.name)

        return


class BrewStatusAction(BrewAction):
    def run(self):
        if not self.shell.available(BREW):
            self.logger.warn("Command is not available: %s" % BREW)
            return

        self.shell.execute([BREW, "tap"])
        self.shell.execute([BREW, "list"])
        return
