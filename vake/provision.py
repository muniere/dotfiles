import glob
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .kernel import Shell
from .timber import Lumber

__all__ = [
    'PrefRecipe', 'PrefBook',
    'SnipRecipe', 'SnipBook',
    'BinPrefBook',
    'ShPrefBook', 'ShSnipBook',
    'BashPrefBook', 'BashSnipBook',
    'ZshPrefBook', 'ZshSnipBook',
    'GitPrefBook',
    'VimPrefBook',
    'AsdfPrefBook',
    'TmuxPrefBook',
    'GradlePrefBook',
    'XcodePrefBook',
    'IntelliJIdeaPrefBook',
    'AndroidStudioPrefBook',
    'AppCodePrefBook',
    'RubyMinePrefBook',
    'GoLandPrefBook',
    'CLionPrefBook',
    'RiderPrefBook',
]


# ==
# Base
# ==
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


@dataclass(frozen=True)
class PrefRecipe:
    src: Path
    dst: Path
    hook: Hook = Hook.noop()

    @staticmethod
    def create(src: str, dst: str, hook: Hook = Hook.noop()) -> 'PrefRecipe':
        return PrefRecipe(src=Path(src), dst=Path(dst), hook=hook)

    @staticmethod
    def glob(src: str, dst: str, hook: Hook = Hook.noop()) -> List['PrefRecipe']:
        pattern = str(Path(dst).expanduser())
        return [
            PrefRecipe(src=Path(src), dst=Path(dst), hook=hook)
            for dst in glob.glob(pattern)
        ]


class PrefBook(metaclass=ABCMeta):
    @property
    @abstractmethod
    def recipes(self) -> List[PrefRecipe]:
        pass


@dataclass
class SnipRecipe:
    src: Path
    dst: Path
    hook: Hook = Hook.noop()

    @staticmethod
    def create(src: str, dst: str, hook: Hook = Hook.noop()) -> 'SnipRecipe':
        return SnipRecipe(src=Path(src), dst=Path(dst), hook=hook)


class SnipBook(metaclass=ABCMeta):
    @property
    @abstractmethod
    def recipes(self) -> List[SnipRecipe]:
        pass


# ==
# Concrete
# ==
class BinPrefBook(PrefBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src="bin",
                dst="~/.bin"
            ),
        ]


class ShPrefBook(PrefBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src="sh.d",
                dst="~/.sh.d"
            ),
        ]


class ShSnipBook(SnipBook):
    @property
    def recipes(self) -> List[SnipRecipe]:
        return [
            SnipRecipe.create(
                src="shrc",
                dst="~/.shrc"
            ),
        ]


class BashPrefBook(PrefBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src="bash.d",
                dst="~/.bash.d"
            ),
            PrefRecipe.create(
                src="bash_completion.d",
                dst="~/.bash_completion.d"
            ),
        ]


class BashSnipBook(SnipBook):
    @property
    def recipes(self) -> List[SnipRecipe]:
        return [
            SnipRecipe.create(
                src="bashrc",
                dst="~/.bashrc"
            ),
            SnipRecipe.create(
                src="bash_profile",
                dst="~/.bash_profile"
            ),
        ]


class ZshPrefBook(PrefBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src="zsh.d",
                dst="~/.zsh.d"
            ),
            PrefRecipe.create(
                src="zsh-completions",
                dst="~/.zsh-completions"
            ),
            PrefRecipe.create(
                src="/usr/local/library/Contributions/brew_zsh_completion.zsh",
                dst="~/.zsh-completions/_brew"
            ),
        ]


class ZshSnipBook(SnipBook):
    @property
    def recipes(self) -> List[SnipRecipe]:
        return [
            SnipRecipe.create(
                src="zshrc",
                dst="~/.zshrc"
            ),
            SnipRecipe.create(
                src="zshprofile",
                dst="~/.zshprofile"
            ),
        ]


class GitPrefBook(PrefBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src="gitconfig",
                dst="~/.gitconfig"
            ),
            PrefRecipe.create(
                src="tigrc",
                dst="~/.tigrc"
            ),
        ]


class VimPrefBook(PrefBook):
    logger: Lumber
    noop: bool

    def __init__(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        super().__init__()
        self.logger = logger
        self.noop = noop

    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src="vimrc",
                dst="~/.vimrc"
            ),
            PrefRecipe.create(
                src="vim",
                dst="~/.vim",
                hook=VimHook(logger=self.logger, noop=self.noop)
            ),
        ]


class VimHook(Hook):
    logger: Lumber
    noop: bool

    def __init__(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        self.logger = logger
        self.noop = noop
        return

    def activate(self):
        dst = Path("~/.vim/autoload/plug.vim").expanduser()
        if dst.is_file():
            self.logger.info(f"Vim-Plug is already downloaded: {dst}")
            return

        shell = Shell(logger=self.logger, noop=self.noop)
        shell.execute([
            "curl",
            "--fail",
            "--location",
            "--create-dirs",
            "--output", str(dst),
            "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim"
        ])

    def deactivate(self):
        pass


class AsdfPrefBook(PrefBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src="asdfrc",
                dst="~/.asdfrc"
            ),
        ]


class TmuxPrefBook(PrefBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src="tmux.conf",
                dst="~/.tmux.conf"
            ),
        ]


class GradlePrefBook(PrefBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src="gradle",
                dst="~/.gradle"
            ),
        ]


class XcodePrefBook(PrefBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src="Xcode",
                dst="~/Library/Developer/Xcode"
            )
        ]


class IntelliJIdeaPrefBook(PrefBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src="IntelliJIdea",
                dst="~/Library/Preferences/IntelliJIdea*"
            ),
            *PrefRecipe.glob(
                src="IntelliJIdea",
                dst="~/Library/ApplicationSupport/JetBrains/IntelliJIdea*"
            ),
        ]


class AndroidStudioPrefBook(PrefBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src="AndroidStudio",
                dst="~/Library/Preferences/AndroidStudio*"
            ),
            *PrefRecipe.glob(
                src="AndroidStudio",
                dst="~/Library/ApplicationSupport/Google/AndroidStudio*"
            ),
        ]


class AppCodePrefBook(PrefBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src="AppCode",
                dst="~/Library/Preferences/AppCode*"
            ),
            *PrefRecipe.glob(
                src="AppCode",
                dst="~/Library/ApplicationSupport/JetBrains/AppCode*"
            ),
        ]


class RubyMinePrefBook(PrefBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src="RubyMine",
                dst="~/Library/Preferences/RubyMine*"
            ),
            *PrefRecipe.glob(
                src="RubyMine",
                dst="~/Library/ApplicationSupport/JetBrains/RubyMine*"
            ),
        ]


class GoLandPrefBook(PrefBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src="GoLand",
                dst="~/Library/Preferences/GoLand*"
            ),
            *PrefRecipe.glob(
                src="GoLand",
                dst="~/Library/ApplicationSupport/JetBrains/GoLand*"
            ),
        ]


class CLionPrefBook(PrefBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src="CLion",
                dst="~/Library/Preferences/CLion*"
            ),
            *PrefRecipe.glob(
                src="CLion",
                dst="~/Library/ApplicationSupport/JetBrains/CLion*"
            ),
        ]


class RiderPrefBook(PrefBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src="Rider",
                dst="~/Library/Preferences/Rider*"
            ),
            *PrefRecipe.glob(
                src="Rider",
                dst="~/Library/ApplicationSupport/JetBrains/Rider*"
            ),
        ]
