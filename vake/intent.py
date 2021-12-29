import glob
import itertools
import os
import re
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Optional, List

from . import filetree
from . import kernel
from . import winston

__all__ = [
    'PrefInstallAction', 'PrefUninstallAction', 'PrefStatusAction',
    'BrewInstallAction', 'BrewUninstallAction', 'BrewStatusAction',
]


# ==
# Base
# ==
class Action(metaclass=ABCMeta):
    noop: bool
    logger: Optional[winston.LoggerWrapper]
    shell: kernel.Shell

    def __init__(self, noop: bool = False, logger: Optional[winston.LoggerWrapper] = None):
        self.noop = noop
        self.logger = logger
        self.shell = kernel.shell(noop, logger)
        return

    @abstractmethod
    def run(self):
        pass


# ==
# Pref
# ==
STATIC_DIR = "./static"
SNIPPET_DIR = "./snippet"


@dataclass
class Recipe:
    src: str
    dst: str
    activate: Optional[Action] = None
    deactivate: Optional[Action] = None

    @staticmethod
    def glob(src: str, dst: str) -> List['Recipe']:
        return [
            Recipe(src=src, dst=dst) for dst in
            glob.glob(os.path.expanduser(dst))
        ]


@dataclass
class Cookbook:
    recipes: List[Recipe]

    @staticmethod
    def bin() -> 'Cookbook':
        return Cookbook([
            Recipe(
                src="bin",
                dst="~/.bin"
            ),
        ])

    @staticmethod
    def sh() -> 'Cookbook':
        return Cookbook([
            Recipe(
                src="sh.d",
                dst="~/.sh.d"
            ),
        ])

    @staticmethod
    def bash() -> 'Cookbook':
        return Cookbook([
            Recipe(
                src="bash.d",
                dst="~/.bash.d"
            ),
            Recipe(
                src="bash_completion.d",
                dst="~/.bash_completion.d"
            ),
        ])

    @staticmethod
    def zsh() -> 'Cookbook':
        return Cookbook([
            Recipe(
                src="zsh.d",
                dst="~/.zsh.d"
            ),
            Recipe(
                src="zsh-completions",
                dst="~/.zsh-completions"
            ),
            Recipe(
                src="/usr/local/library/Contributions/brew_zsh_completion.zsh",
                dst="~/.zsh-completions/_brew"
            ),
        ])

    @staticmethod
    def git() -> 'Cookbook':
        return Cookbook([
            Recipe(
                src="gitconfig",
                dst="~/.gitconfig"
            ),
            Recipe(
                src="tigrc",
                dst="~/.tigrc"
            ),
        ])

    @staticmethod
    def vim(noop: bool = False, logger: Optional[winston.LoggerWrapper] = None) -> 'Cookbook':
        return Cookbook([
            Recipe(
                src="vimrc",
                dst="~/.vimrc"
            ),
            Recipe(
                src="vim",
                dst="~/.vim",
                activate=VimActivateAction(noop=noop, logger=logger),
                deactivate=VimDeactivateAction(noop=noop, logger=logger)
            ),
        ])

    @staticmethod
    def asdf() -> 'Cookbook':
        return Cookbook([
            Recipe(
                src="asdfrc",
                dst="~/.asdfrc"
            ),
        ])

    @staticmethod
    def tmux() -> 'Cookbook':
        return Cookbook([
            Recipe(
                src="tmux.conf",
                dst="~/.tmux.conf"
            ),
        ])

    @staticmethod
    def gradle() -> 'Cookbook':
        return Cookbook([
            Recipe(
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
        if kernel.islinux():
            books += []

        # darwin
        if kernel.isdarwin():
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
            Recipe(
                src="shrc",
                dst="~/.shrc"
            ),

            # bash
            Recipe(
                src="bashrc",
                dst="~/.bashrc"
            ),
            Recipe(
                src="bash_profile",
                dst="~/.bash_profile"
            ),

            # zsh
            Recipe(
                src="zshrc",
                dst="~/.zshrc"
            ),
            Recipe(
                src="zshprofile",
                dst="~/.zshprofile"
            ),
        ]


class PrefInstallAction(PrefAction):
    def run(self):
        for recipe in self.recipes():
            if recipe.src.startswith('/'):
                self.__run(recipe)
            else:
                self.__run(recipe, sysname=kernel.sysname())
                self.__run(recipe, sysname="default")

            if recipe.activate:
                recipe.activate.run()

        for snippet in self.snippets():
            self.__enable(snippet)

        return

    def __run(self, recipe: Recipe, sysname="default") -> bool:
        if not self.__istarget(recipe):
            if self.logger:
                relpath = filetree.pilot(recipe.src) \
                    .prepend(sysname) \
                    .prepend(STATIC_DIR) \
                    .relpath(os.getcwd())
                self.logger.info("File is not target: %s" % relpath)
            return False

        if recipe.src.startswith('/'):
            src = filetree.pilot(recipe.src)
        else:
            src = filetree.pilot(recipe.src) \
                .prepend(sysname) \
                .prepend(STATIC_DIR).abspath()

        if recipe.dst.startswith('/'):
            dst = filetree.pilot(recipe.dst)
        else:
            dst = filetree.pilot(recipe.dst).expanduser()

        #
        # guard
        #

        # src not found
        if not src.exists():
            return False

        # dst link already exists
        if dst.islink():
            if self.logger:
                self.logger.info(
                    "Symlink already exists: %s" % dst.reduceuser()
                )
            return False

        #
        # file
        #
        if src.isfile():
            # another file already exists
            if dst.isfile():
                if self.logger:
                    self.logger.info(
                        "File already exists: %s" % dst.reduceuser()
                    )
                return False

            # ensure parent directory
            dst_dir = dst.parent()
            if not dst_dir.isdir():
                self.shell.mkdir(dst_dir.pathname(), recursive=True)

            # create symbolic link
            return self.shell.symlink(src.pathname(), dst.pathname(), force=True)

        #
        # directory
        #
        if src.isdir():
            for new_src in src.children(target='f', recursive=True):
                new_dst = filetree.pilot(recipe.dst) \
                    .append(new_src.relpath(src))
                new_recipe = Recipe(
                    src=new_src.pathname(),
                    dst=new_dst.pathname()
                )
                self.__run(new_recipe, sysname=sysname)

        return True

    def __enable(self, snippet: Recipe):

        #
        # source
        #
        src = filetree.pilot(snippet.src).prepend(SNIPPET_DIR)

        if not src.exists():
            return

        src_str = src.read().strip()

        #
        # destination
        #
        dst = filetree.pilot(snippet.dst).expanduser()

        # new file
        if not dst.exists():
            if self.logger:
                self.logger.execute("Enable snippet %s" % src.reduceuser())

            if not self.noop:
                dst.write(src_str + "\n")

            return

        dst_str = dst.read()

        # skip: already enabled
        if src_str in dst_str:
            if self.logger:
                self.logger.info(
                    "Snippet already enabled: %s" % dst.reduceuser()
                )
            return

        # enable
        if self.logger:
            self.logger.execute("Enable %s" % src.reduceuser())

        if not self.noop:
            dst.write(dst_str + src_str + "\n")

        return

    @staticmethod
    def __istarget(recipe: Recipe):
        blacklist = [r'\.swp$', r'\.bak$', r'\.DS_Store$']

        for pattern in blacklist:
            if re.search(pattern, recipe.src):
                return False

        return True


class PrefUninstallAction(PrefAction):
    def run(self):
        for linker in self.recipes():
            self.__run(linker, sysname=kernel.sysname())
            self.__run(linker, sysname="default")

            if linker.deactivate:
                linker.deactivate.run()

        for snippet in self.snippets():
            self.__disable(snippet)

        return

    def __run(self, recipe: Recipe, sysname: str = "default") -> bool:
        if not self.__istarget(recipe):
            if self.logger:
                relpath = filetree.pilot(recipe.src) \
                    .prepend(sysname) \
                    .prepend(STATIC_DIR) \
                    .relpath(os.getcwd())
                self.logger.info("File is not target: %s" % relpath)
            return False

        if recipe.src.startswith('/'):
            src = filetree.pilot(recipe.src)
        else:
            src = filetree.pilot(recipe.src) \
                .prepend(sysname) \
                .prepend(STATIC_DIR).abspath()

        if recipe.dst.startswith('/'):
            dst = filetree.pilot(recipe.dst)
        else:
            dst = filetree.pilot(recipe.dst).expanduser()

        #
        # guard
        #

        # src not found
        if not src.exists():
            return True

        # dst not found
        if not dst.exists() and not dst.islink():
            if self.logger:
                self.logger.info("File already removed: %s" % dst)
            return True

        #
        # symlink
        #
        if dst.islink():
            return self.shell.remove(dst.pathname())

        #
        # file
        #
        if dst.isfile():
            if self.logger:
                self.logger.info("File is not symlink: %s" % dst)
            return False

        #
        # directory
        #
        if src.isdir():
            for new_src in src.children(target='f', recursive=True):
                new_dst = filetree.pilot(recipe.dst) \
                    .append(new_src.relpath(src))
                new_recipe = Recipe(
                    src=new_src.pathname(),
                    dst=new_dst.pathname()
                )
                self.__run(new_recipe, sysname=sysname)

        return True

    def __disable(self, snippet: Recipe):

        #
        # source
        #
        src = filetree.pilot(snippet.src).prepend(SNIPPET_DIR)

        if not src.exists():
            return

        src_str = src.read().strip()

        #
        # destination
        #
        dst = filetree.pilot(snippet.dst).expanduser()

        # not found
        if not dst.exists():
            self.logger.info("File NOT FOUND: %s" % dst.reduceuser())
            return

        dst_str = dst.read()

        # skip: already disabled
        if src_str not in dst_str:
            if self.logger:
                self.logger.info(
                    "Snippet already disabled: %s" % dst.reduceuser()
                )
            return

        # disable
        if self.logger:
            self.logger.execute("Disable snippet %s" % src.reduceuser())

        if not self.noop:
            dst.write(dst_str.replace(src_str, ""))

        return

    @staticmethod
    def __istarget(recipe: Recipe):
        blacklist = [r'\.swp$', r'\.DS_Store$']

        for pattern in blacklist:
            if re.search(pattern, recipe.src):
                return False

        return True


class PrefStatusAction(PrefAction):
    def run(self):
        linkers = sorted(self.recipes(), key=lambda x: x.dst)

        for dot in linkers:
            target = filetree.pilot(dot.dst).expanduser()

            if not target.exists():
                continue

            if kernel.isdarwin():
                self.shell.execute("ls -lFG %s" % target)
            else:
                self.shell.execute("ls -lFo %s" % target)

        return True


class VimActivateAction(Action):

    def run(self):
        dst = filetree.pilot("~/.vim/autoload/plug.vim").expanduser()

        if dst.isfile():
            self.logger.info(
                "Vim-Plug is already downloaded: %s" % dst.reduceuser()
            )
            return None

        self.shell.execute([
            "curl",
            "--fail",
            "--location",
            "--create-dirs",
            "--output", str(dst),
            "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim"
        ])
        return None


class VimDeactivateAction(Action):

    def run(self):
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
        src = filetree.pilot(os.getcwd()) \
            .append(STATIC_DIR) \
            .append(kernel.sysname()) \
            .append(BREWFILE)

        if self.logger:
            self.logger.debug("Read kegs from file: %s" % src)

        if not src.exists():
            return []

        lines = src.readlines()
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
