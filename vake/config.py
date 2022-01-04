import glob
import tempfile
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from . import shell
from .timber import Lumber

__all__ = [
    'PrefChain', 'PrefRecipe', 'PrefBook',
    'SnipRecipe', 'SnipBook',
    'BinPrefBook',
    'ShPrefBook', 'ShSnipBook',
    'BashPrefBook', 'BashSnipBook',
    'ZshPrefBook', 'ZshSnipBook',
    'VimPrefBook',
    'GitPrefBook', 'GitHubPrefBook',
    'AsdfPrefBook',
    'TmuxPrefBook',
    'GradlePrefBook',
    'BrewPrefBook',
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
class PrefChain:
    src: Path
    dst: Path


@dataclass(frozen=True)
class PrefRecipe:
    src: Path
    dst: Path
    hook: Hook = Hook.noop()
    private: bool = False

    @staticmethod
    def create(
        src: str,
        dst: str,
        hook: Hook = Hook.noop(),
        private: bool = False,
    ) -> 'PrefRecipe':
        return PrefRecipe(src=Path(src), dst=Path(dst), hook=hook, private=private)

    @staticmethod
    def glob(
        src: str,
        dst: str,
        hook: Hook = Hook.noop(),
        private: bool = False,
    ) -> list['PrefRecipe']:
        pattern = str(Path(dst).expanduser())
        return [
            PrefRecipe(src=Path(src), dst=Path(dst), hook=hook, private=private)
            for dst in glob.glob(pattern)
        ]

    def expand(self, src_prefix: Path = Path(), dst_prefix: Path = Path()) -> list[PrefChain]:
        # resolve
        ex_src = self.src.expanduser()

        if ex_src.is_absolute():
            abs_src = Path(ex_src)
        else:
            abs_src = Path(src_prefix, ex_src).resolve()

        ex_dst = self.dst.expanduser()

        if ex_dst.is_absolute():
            abs_dst = Path(ex_dst)
        else:
            abs_dst = Path(dst_prefix, ex_dst).resolve()

        # guard : none
        if not abs_src.exists():
            return []

        # expand : file
        if abs_src.is_file():
            return [
                PrefChain(src=abs_src, dst=abs_dst)
            ]

        # expand
        abs_dir = abs_src

        return [
            PrefChain(
                src=abs_file,
                dst=Path(abs_dst, abs_file.relative_to(abs_dir)),
            )
            for abs_file in [x for x in abs_dir.glob('**/*') if x.is_file()]
        ]


class PrefBook(metaclass=ABCMeta):
    @property
    @abstractmethod
    def recipes(self) -> list[PrefRecipe]:
        pass


@dataclass
class SnipRecipe:
    src: Path
    dst: Path

    @staticmethod
    def create(src: str, dst: str) -> 'SnipRecipe':
        return SnipRecipe(src=Path(src), dst=Path(dst))


class SnipBook(metaclass=ABCMeta):
    @property
    @abstractmethod
    def recipes(self) -> list[SnipRecipe]:
        pass


# ==
# Concrete
# ==
class BinPrefBook(PrefBook):
    @property
    def recipes(self) -> list[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='bin',
                dst='~/.bin'
            ),
        ]


class ShPrefBook(PrefBook):
    @property
    def recipes(self) -> list[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='sh.d',
                dst='~/.sh.d'
            ),
        ]


class ShSnipBook(SnipBook):
    @property
    def recipes(self) -> list[SnipRecipe]:
        return [
            SnipRecipe.create(
                src='shrc',
                dst='~/.shrc'
            ),
        ]


class BashPrefBook(PrefBook):
    @property
    def recipes(self) -> list[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='bash.d',
                dst='~/.bash.d'
            ),
            PrefRecipe.create(
                src='bash_completion.d',
                dst='~/.bash_completion.d'
            ),
            PrefRecipe.create(
                src='/Applications/Docker.app/Contents/Resources/etc/docker.bash-completion',
                dst='/usr/local/etc/bash_completion.d/docker'
            ),
            PrefRecipe.create(
                src='/Applications/Docker.app/Contents/Resources/etc/docker-compose.bash-completion',
                dst='/usr/local/etc/bash_completion.d/docker-compose'
            ),
            PrefRecipe.create(
                src='/Applications/Docker.app/Contents/Resources/etc/docker.zsh-completion',
                dst='/usr/local/share/zsh/site-functions/_docker'
            ),
            PrefRecipe.create(
                src='/Applications/Docker.app/Contents/Resources/etc/docker-compose.zsh-completion',
                dst='/usr/local/share/zsh/site-functions/_docker-compose'
            ),
        ]


class BashSnipBook(SnipBook):
    @property
    def recipes(self) -> list[SnipRecipe]:
        return [
            SnipRecipe.create(
                src='bashrc',
                dst='~/.bashrc'
            ),
            SnipRecipe.create(
                src='bash_profile',
                dst='~/.bash_profile'
            ),
        ]


class ZshPrefBook(PrefBook):
    logger: Lumber
    noop: bool

    def __init__(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        super().__init__()
        self.logger = logger
        self.noop = noop

    @property
    def recipes(self) -> list[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='zsh.d',
                dst='~/.zsh.d',
                hook=ZshHook(logger=self.logger, noop=self.noop)
            ),
            PrefRecipe.create(
                src='zsh-completions',
                dst='~/.zsh-completions'
            ),
            PrefRecipe.create(
                src='/usr/local/library/Contributions/brew_zsh_completion.zsh',
                dst='~/.zsh-completions/_brew'
            ),
        ]


class ZshHook(Hook):
    logger: Lumber
    noop: bool

    def __init__(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        self.logger = logger
        self.noop = noop
        return

    def activate(self):
        dst = Path('~/.local/share/zinit/zinit.git').expanduser()
        if dst.exists():
            self.logger.info(f'Zinit is already downloaded: {dst}')
            return

        with tempfile.NamedTemporaryFile() as tmp:
            shell.call(
                args=[
                    'curl',
                    '--fail',
                    '--silent',
                    '--show-error',
                    '--location',
                    '--output', tmp.name,
                    'https://git.io/zinit-install'
                ],
                logger=self.logger,
                noop=self.noop,
            )

            shell.call(
                args=['sh', tmp.name],
                env={'NO_EDIT': '1'},
                logger=self.logger,
                noop=self.noop,
            )

        pass

    def deactivate(self):
        pass


class ZshSnipBook(SnipBook):
    @property
    def recipes(self) -> list[SnipRecipe]:
        return [
            SnipRecipe.create(
                src='zshrc',
                dst='~/.zshrc'
            ),
            SnipRecipe.create(
                src='zshprofile',
                dst='~/.zshprofile'
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
    def recipes(self) -> list[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='vimrc',
                dst='~/.vimrc'
            ),
            PrefRecipe.create(
                src='vim',
                dst='~/.vim',
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
        dst = Path('~/.vim/autoload/plug.vim').expanduser()
        if dst.is_file():
            self.logger.info(f'Vim-Plug is already downloaded: {dst}')
            return

        shell.call(
            args=[
                'curl',
                '--fail',
                '--location',
                '--create-dirs',
                '--output', str(dst),
                'https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'
            ],
            logger=self.logger,
            noop=self.noop,
        )

    def deactivate(self):
        pass


class GitPrefBook(PrefBook):
    @property
    def recipes(self) -> list[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='gitconfig',
                dst='~/.gitconfig'
            ),
            PrefRecipe.create(
                src='tigrc',
                dst='~/.tigrc'
            ),
        ]


class GitHubPrefBook(PrefBook):
    @property
    def recipes(self) -> list[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='gh-extensions',
                dst='~/.local/share/gh/extensions'
            ),
        ]


class AsdfPrefBook(PrefBook):
    @property
    def recipes(self) -> list[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='asdfrc',
                dst='~/.asdfrc'
            ),
        ]


class TmuxPrefBook(PrefBook):
    @property
    def recipes(self) -> list[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='tmux.conf',
                dst='~/.tmux.conf'
            ),
        ]


class GradlePrefBook(PrefBook):
    @property
    def recipes(self) -> list[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='gradle',
                dst='~/.gradle',
                private=True,
            ),
        ]


class BrewPrefBook(PrefBook):
    logger: Lumber
    noop: bool

    def __init__(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        super().__init__()
        self.logger = logger
        self.noop = noop

    @property
    def recipes(self) -> list[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='Brewfile',
                dst='~/.Brewfile',
                hook=BrewHook(logger=self.logger, noop=self.noop)
            ),
        ]


class BrewHook(Hook):
    logger: Lumber
    noop: bool

    def __init__(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        super().__init__()
        self.logger = logger
        self.noop = noop

    # noinspection PyBroadException
    def activate(self):
        try:
            shell.which('brew')
        except shell.SubprocessError:
            self.logger.warn('skip bundle. command not found: brew')
            return

        self.logger.info('Checking if all kegs are installed ...')

        proc = shell.run(
            args=['brew', 'bundle', 'check', '--global']
        )
        if proc.returncode == 0:
            self.logger.info('All kegs are satisfied.')
            return

        shell.call(
            args=['brew', 'bundle', 'install', '--global'],
            logger=self.logger,
            noop=self.noop,
        )

    def deactivate(self):
        pass


class XcodePrefBook(PrefBook):
    @property
    def recipes(self) -> list[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='Xcode',
                dst='~/Library/Developer/Xcode',
                private=True,
            )
        ]


class IntelliJIdeaPrefBook(PrefBook):
    @property
    def recipes(self) -> list[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='IntelliJIdea',
                dst='~/Library/Preferences/IntelliJIdea*',
                private=True,
            ),
            *PrefRecipe.glob(
                src='IntelliJIdea',
                dst='~/Library/ApplicationSupport/JetBrains/IntelliJIdea*',
                private=True,
            ),
        ]


class AndroidStudioPrefBook(PrefBook):
    @property
    def recipes(self) -> list[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='AndroidStudio',
                dst='~/Library/Preferences/AndroidStudio*',
                private=True,
            ),
            *PrefRecipe.glob(
                src='AndroidStudio',
                dst='~/Library/ApplicationSupport/Google/AndroidStudio*',
                private=True,
            ),
        ]


class AppCodePrefBook(PrefBook):
    @property
    def recipes(self) -> list[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='AppCode',
                dst='~/Library/Preferences/AppCode*',
                private=True,
            ),
            *PrefRecipe.glob(
                src='AppCode',
                dst='~/Library/ApplicationSupport/JetBrains/AppCode*',
                private=True,
            ),
        ]


class RubyMinePrefBook(PrefBook):
    @property
    def recipes(self) -> list[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='RubyMine',
                dst='~/Library/Preferences/RubyMine*',
                private=True,
            ),
            *PrefRecipe.glob(
                src='RubyMine',
                dst='~/Library/ApplicationSupport/JetBrains/RubyMine*',
                private=True,
            ),
        ]


class GoLandPrefBook(PrefBook):
    @property
    def recipes(self) -> list[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='GoLand',
                dst='~/Library/Preferences/GoLand*',
                private=True,
            ),
            *PrefRecipe.glob(
                src='GoLand',
                dst='~/Library/ApplicationSupport/JetBrains/GoLand*',
                private=True,
            ),
        ]


class CLionPrefBook(PrefBook):
    @property
    def recipes(self) -> list[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='CLion',
                dst='~/Library/Preferences/CLion*',
                private=True,
            ),
            *PrefRecipe.glob(
                src='CLion',
                dst='~/Library/ApplicationSupport/JetBrains/CLion*',
                private=True,
            ),
        ]


class RiderPrefBook(PrefBook):
    @property
    def recipes(self) -> list[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='Rider',
                dst='~/Library/Preferences/Rider*',
                private=True,
            ),
            *PrefRecipe.glob(
                src='Rider',
                dst='~/Library/ApplicationSupport/JetBrains/Rider*',
                private=True,
            ),
        ]
