import glob
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List

from . import shell
from .box import TernaryBox
from .timber import Lumber

__all__ = [
    'PrefChain', 'PrefRecipe',
    'SnipRecipe', 'CookBook',
    'BinCookBook',
    'ShCookBook',
    'BashCookBook',
    'ZshCookBook',
    'VimCookBook',
    'GitCookBook', 'GitHubCookBook',
    'AsdfCookBook',
    'TmuxCookBook',
    'GradleCookBook',
    'BrewCookBook',
    'XcodeCookBook',
    'IntelliJIdeaCookBook',
    'AndroidStudioCookBook',
    'AppCodeCookBook',
    'RubyMineCookBook',
    'GoLandCookBook',
    'CLionCookBook',
    'RiderCookBook',
]


# ==
# Base
# ==
@dataclass(frozen=True)
class PrefChain:
    src: Path
    dst: Path

    def resolve_src(self, *other):
        try:
            return self.src.relative_to(*other)
        except ValueError:
            return self.src

    def resolve_dst(self):
        if self.dst.exists():
            return self.dst
        else:
            return Path('(null)')


@dataclass(frozen=True)
class PrefRecipe:
    src: Path
    dst: Path

    @staticmethod
    def create(src: str, dst: str) -> 'PrefRecipe':
        return PrefRecipe(src=Path(src), dst=Path(dst))

    @staticmethod
    def glob(src: str, dst: str) -> List['PrefRecipe']:
        pattern = str(Path(dst).expanduser())
        return [
            PrefRecipe(src=Path(src), dst=Path(dst))
            for dst in glob.glob(pattern)
        ]

    def expand(self, src_prefix: Path = Path(), dst_prefix: Path = Path()) -> List[PrefChain]:
        # resolve
        ex_src = self.src.expanduser()
        abs_src = TernaryBox(ex_src.is_absolute()).fold(
            some=lambda: Path(ex_src),
            none=lambda: Path(src_prefix, ex_src).resolve(),
        )

        ex_dst = self.dst.expanduser()
        abs_dst = TernaryBox(ex_dst.is_absolute()).fold(
            some=lambda: Path(ex_dst),
            none=lambda: Path(dst_prefix, ex_dst).resolve(),
        )

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


@dataclass
class SnipRecipe:
    src: Path
    dst: Path

    @staticmethod
    def create(src: str, dst: str) -> 'SnipRecipe':
        return SnipRecipe(src=Path(src), dst=Path(dst))


class CookBook(metaclass=ABCMeta):
    @property
    def name(self) -> str:
        return type(self).__name__

    @property
    @abstractmethod
    def recipes(self) -> List[PrefRecipe]:
        raise NotImplementedError()

    @property
    def snippets(self) -> List[SnipRecipe]:
        return []

    @property
    def private(self) -> bool:
        return False

    def activate(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        pass

    def deactivate(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        pass

    @staticmethod
    def _mkdir(path: Path, logger: Lumber = Lumber.noop(), noop: bool = False) -> bool:
        logger.trace(f'mkdir -p {path}')

        if noop:
            return False

        path.mkdir(parents=True, exist_ok=True)
        return True

    @staticmethod
    def _touch(path: Path, logger: Lumber = Lumber.noop(), noop: bool = False) -> bool:
        logger.trace(f'touch {path}')

        if noop:
            return False

        path.touch(exist_ok=True)
        return True


# ==
# Concrete
# ==
class BinCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='bin/',
                dst='~/.local/bin'
            ),
        ]


class ShCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='sh.d/',
                dst='~/.sh.d'
            ),
        ]

    @property
    def snippets(self) -> List[SnipRecipe]:
        return [
            SnipRecipe.create(
                src='shrc/',
                dst='~/.shrc'
            ),
        ]


class BashCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='bash.d/',
                dst='~/.bash.d'
            ),
            PrefRecipe.create(
                src='bash_completion.d/',
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

    @property
    def snippets(self) -> List[SnipRecipe]:
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


class ZshCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='zsh.d/',
                dst='~/.zsh.d',
            ),
            PrefRecipe.create(
                src='zsh-completions/',
                dst='~/.zsh-completions'
            ),
            PrefRecipe.create(
                src='/usr/local/library/Contributions/brew_zsh_completion.zsh',
                dst='~/.zsh-completions/_brew'
            ),
        ]

    @property
    def snippets(self) -> List[SnipRecipe]:
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

    def activate(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        url = 'https://git.io/zinit-install'

        shell.call(
            cmd=f'sh -c "NO_EMOJI=1 NO_EDIT=1 NO_TUTORIAL=1 $(curl -fSL {url})"',
            logger=logger,
            noop=noop,
        )

        try:
            shell.which('zsh')
        except shell.SubprocessError:
            logger.warn('skip updating zsh plugins. command not found: zsh')
            return

        shell.call(
            cmd='zsh -i -c "zinit update --all"',
            logger=logger,
            noop=noop,
        )
        return


class VimCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='vim/',
                dst='~/.vim',
            ),
        ]

    def activate(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        url = 'https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'
        out = '~/.vim/autoload/plug.vim'

        shell.call(
            cmd=f'sh -c "curl -fSL -o {out} --create-dirs {url}"',
            logger=logger,
            noop=noop,
        )

        try:
            shell.which('vim')
        except shell.SubprocessError:
            logger.warn('skip updating vim plugins. command not found: vim')
            return

        shell.call(
            cmd='vim +PlugInstall +qall >/dev/null 2>&1',
            logger=logger,
            noop=noop,
        )

        return


class GitCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='git/',
                dst='~/.config/git'
            ),
            PrefRecipe.create(
                src='tig/',
                dst='~/.config/tig'
            ),
        ]

    def activate(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        hist = Path('~/.local/share/tig/history').expanduser()

        if not hist.parent.is_dir():
            self._mkdir(hist.parent, logger=logger, noop=noop)

        self._touch(hist, logger=logger, noop=noop)


class GitHubCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='gh/',
                dst='~/.local/share/gh'
            ),
        ]


class AsdfCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='asdf/',
                dst='~/.config/asdf'
            ),
        ]


class TmuxCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='tmux/',
                dst='~/.config/tmux'
            ),
        ]


class RangerCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='ranger/',
                dst='~/.config/ranger'
            ),
        ]


class GradleCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='gradle',
                dst='~/.gradle',
            ),
        ]

    @property
    def private(self) -> bool:
        return True


class RubyCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='bundle/',
                dst='~/.config/bundle'
            ),
        ]


class NodeCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='npm/',
                dst='~/.config/npm'
            ),
        ]

    def activate(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        hist = Path('~/.local/share/node/history').expanduser()

        if not hist.parent.is_dir():
            self._mkdir(hist.parent, logger=logger, noop=noop)

        self._touch(hist, logger=logger, noop=noop)


class BrewCookBook(CookBook):

    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            PrefRecipe.create(
                src='Brewfile',
                dst='~/.config/homebrew/Brewfile',
            ),
        ]

    # noinspection PyBroadException
    def activate(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        try:
            shell.which('brew')
        except shell.SubprocessError:
            logger.warn('skip bundle. command not found: brew')
            return

        shell.call(
            cmd='brew bundle install --file ~/.config/homebrew/Brewfile --no-lock',
            logger=logger,
            noop=noop,
        )

        return


class XcodeCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='Xcode/',
                dst='~/Library/Developer/Xcode',
            )
        ]

    @property
    def private(self) -> bool:
        return True


class IntelliJIdeaCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='IntelliJIdea/',
                dst='~/Library/Preferences/IntelliJIdea*',
            ),
            *PrefRecipe.glob(
                src='IntelliJIdea/',
                dst='~/Library/ApplicationSupport/JetBrains/IntelliJIdea*',
            ),
        ]

    @property
    def private(self) -> bool:
        return True


class AndroidStudioCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='AndroidStudio/',
                dst='~/Library/Preferences/AndroidStudio*',
            ),
            *PrefRecipe.glob(
                src='AndroidStudio/',
                dst='~/Library/ApplicationSupport/Google/AndroidStudio*',
            ),
        ]

    @property
    def private(self) -> bool:
        return True


class AppCodeCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='AppCode/',
                dst='~/Library/Preferences/AppCode*',
            ),
            *PrefRecipe.glob(
                src='AppCode/',
                dst='~/Library/ApplicationSupport/JetBrains/AppCode*',
            ),
        ]

    @property
    def private(self) -> bool:
        return True


class RubyMineCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='RubyMine/',
                dst='~/Library/Preferences/RubyMine*',
            ),
            *PrefRecipe.glob(
                src='RubyMine/',
                dst='~/Library/ApplicationSupport/JetBrains/RubyMine*',
            ),
        ]

    @property
    def private(self) -> bool:
        return True


class GoLandCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='GoLand/',
                dst='~/Library/Preferences/GoLand*',
            ),
            *PrefRecipe.glob(
                src='GoLand/',
                dst='~/Library/ApplicationSupport/JetBrains/GoLand*',
            ),
        ]

    @property
    def private(self) -> bool:
        return True


class CLionCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='CLion/',
                dst='~/Library/Preferences/CLion*',
            ),
            *PrefRecipe.glob(
                src='CLion/',
                dst='~/Library/ApplicationSupport/JetBrains/CLion*',
            ),
        ]

    @property
    def private(self) -> bool:
        return True


class RiderCookBook(CookBook):
    @property
    def recipes(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='Rider/',
                dst='~/Library/Preferences/Rider*',
            ),
            *PrefRecipe.glob(
                src='Rider/',
                dst='~/Library/ApplicationSupport/JetBrains/Rider*',
            ),
        ]

    @property
    def private(self) -> bool:
        return True
