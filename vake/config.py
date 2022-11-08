import glob
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set

from . import flow
from . import shell
from . import xdglib
from .timber import Lumber

__all__ = [
    'PrefChain', 'PrefRecipe',
    'SnipChain', 'SnipRecipe',
    'CookBook',
    'BinCookBook',
    'ShCookBook',
    'BashCookBook',
    'ZshCookBook',
    'VimCookBook',
    'GitCookBook', 'GitHubCookBook',
    'AsdfCookBook',
    'TmuxCookBook',
    'GradleCookBook',
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
        abs_src = flow.branch(
            value=ex_src.is_absolute(),
            truthy=lambda: Path(ex_src),
            falsy=lambda: Path(src_prefix, ex_src).resolve(),
        )

        ex_dst = self.dst.expanduser()
        abs_dst = flow.branch(
            value=ex_dst.is_absolute(),
            truthy=lambda: Path(ex_dst),
            falsy=lambda: Path(dst_prefix, ex_dst).resolve(),
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


@dataclass(frozen=True)
class SnipChain:
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


@dataclass
class SnipRecipe:
    src: Path
    dst: Path

    @staticmethod
    def create(src: str, dst: str) -> 'SnipRecipe':
        return SnipRecipe(src=Path(src), dst=Path(dst))

    def expand(self, src_prefix: Path = Path(), dst_prefix: Path = Path()) -> List[SnipChain]:
        # resolve
        ex_src = self.src.expanduser()
        abs_src = flow.branch(
            value=ex_src.is_absolute(),
            truthy=lambda: Path(ex_src),
            falsy=lambda: Path(src_prefix, ex_src).resolve(),
        )

        ex_dst = self.dst.expanduser()
        abs_dst = flow.branch(
            value=ex_dst.is_absolute(),
            truthy=lambda: Path(ex_dst),
            falsy=lambda: Path(dst_prefix, ex_dst).resolve(),
        )

        # guard : none
        if not abs_src.exists():
            return []

        # expand : file
        if abs_src.is_file():
            return [
                SnipChain(src=abs_src, dst=abs_dst)
            ]

        # expand
        abs_dir = abs_src

        return [
            SnipChain(
                src=abs_file,
                dst=Path(abs_dst, abs_file.relative_to(abs_dir)),
            )
            for abs_file in [x for x in abs_dir.glob('**/*') if x.is_file()]
        ]


class CookBook(metaclass=ABCMeta):
    @property
    def name(self) -> str:
        return type(self).__name__

    @property
    @abstractmethod
    def aliases(self) -> Set[str]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def prefs(self) -> List[PrefRecipe]:
        raise NotImplementedError()

    @property
    def snips(self) -> List[SnipRecipe]:
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
    def aliases(self) -> Set[str]:
        return {'bin'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            PrefRecipe(
                src=Path('bin/'),
                dst=xdglib.bin_()
            ),
        ]


class ShCookBook(CookBook):
    @property
    def aliases(self) -> Set[str]:
        return {'sh'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            PrefRecipe(
                src=Path('sh/'),
                dst=xdglib.config('sh/')
            ),
        ]

    def activate(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        shell.call(
            cmd=f'mkdir -p -m 755 {xdglib.bin_()}',
            logger=logger,
            noop=noop,
        )
        shell.call(
            cmd=f'mkdir -p -m 755 {xdglib.cache()}',
            logger=logger,
            noop=noop,
        )
        shell.call(
            cmd=f'mkdir -p -m 755 {xdglib.config()}',
            logger=logger,
            noop=noop,
        )
        shell.call(
            cmd=f'mkdir -p -m 755 {xdglib.data()}',
            logger=logger,
            noop=noop,
        )
        shell.call(
            cmd=f'mkdir -p -m 755 {xdglib.state()}',
            logger=logger,
            noop=noop,
        )
        shell.call(
            cmd=f'mkdir -p -m 700 {xdglib.runtime()}',
            logger=logger,
            noop=noop,
        )


class BashCookBook(CookBook):
    @property
    def aliases(self) -> Set[str]:
        return {'bash'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            PrefRecipe(
                src=Path('bash/'),
                dst=xdglib.config('bash/')
            ),
            PrefRecipe(
                src=Path('/Applications/Docker.app/Contents/Resources/etc/docker.bash-completion'),
                dst=xdglib.data('bash/bash_completion.d/docker')
            ),
            PrefRecipe(
                src=Path('/Applications/Docker.app/Contents/Resources/etc/docker-compose.bash-completion'),
                dst=xdglib.data('bash/bash_completion.d/docker-compose')
            ),
        ]

    @property
    def snips(self) -> List[SnipRecipe]:
        return [
            SnipRecipe.create(
                src='bashrc',
                dst='~/.bashrc'
            ),
        ]


class ZshCookBook(CookBook):
    @property
    def aliases(self) -> Set[str]:
        return {'zsh'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            PrefRecipe(
                src=Path('zsh/'),
                dst=xdglib.config('zsh/'),
            ),
            PrefRecipe(
                src=Path('zsh-site-functions/'),
                dst=xdglib.data('zsh/site-functions/')
            ),
            PrefRecipe(
                src=Path('/Applications/Docker.app/Contents/Resources/etc/docker.zsh-completion'),
                dst=xdglib.data('zsh/site-functions/_docker')
            ),
            PrefRecipe(
                src=Path('/Applications/Docker.app/Contents/Resources/etc/docker-compose.zsh-completion'),
                dst=xdglib.data('zsh/site-functions/_docker-compose')
            ),
        ]

    @property
    def snips(self) -> List[SnipRecipe]:
        return [
            SnipRecipe.create(
                src='zshenv',
                dst='~/.zshenv'
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
    def aliases(self) -> Set[str]:
        return {'vim'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            PrefRecipe(
                src=Path('vim/'),
                dst=xdglib.config('vim/'),
            ),
        ]

    @property
    def snips(self) -> List[SnipRecipe]:
        return [
            SnipRecipe.create(
                src='vimrc',
                dst='~/.vimrc'
            ),
        ]

    def activate(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        url = 'https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'
        out = xdglib.config('vim/autoload/plug.vim')

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
    def aliases(self) -> Set[str]:
        return {'git'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            PrefRecipe(
                src=Path('git/'),
                dst=xdglib.config('git/')
            ),
            PrefRecipe(
                src=Path('tig/'),
                dst=xdglib.config('tig/')
            ),
        ]

    def activate(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        hist = xdglib.config('tig/history')

        if not hist.parent.is_dir():
            self._mkdir(hist.parent, logger=logger, noop=noop)

        self._touch(hist, logger=logger, noop=noop)


class GitHubCookBook(CookBook):
    @property
    def aliases(self) -> Set[str]:
        return {'github'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            PrefRecipe(
                src=Path('gh/'),
                dst=xdglib.data('gh/')
            ),
        ]


class AsdfCookBook(CookBook):
    @property
    def aliases(self) -> Set[str]:
        return {'asdf'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            PrefRecipe(
                src=Path('asdf/'),
                dst=xdglib.config('asdf/')
            ),
        ]


class TmuxCookBook(CookBook):
    @property
    def aliases(self) -> Set[str]:
        return {'tmux'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            PrefRecipe(
                src=Path('tmux/'),
                dst=xdglib.config('tmux/')
            ),
        ]


class RangerCookBook(CookBook):
    @property
    def aliases(self) -> Set[str]:
        return {'ranger'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            PrefRecipe(
                src=Path('ranger/'),
                dst=xdglib.config('ranger/')
            ),
        ]


class GradleCookBook(CookBook):
    @property
    def aliases(self) -> Set[str]:
        return {'gradle'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            PrefRecipe(
                src=Path('gradle'),
                dst=xdglib.data('gradle/'),
            ),
        ]

    @property
    def private(self) -> bool:
        return True


class PythonCookBook(CookBook):
    @property
    def aliases(self) -> Set[str]:
        return {'python'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            PrefRecipe(
                src=Path('python/'),
                dst=xdglib.config('python/')
            ),
        ]


class RubyCookBook(CookBook):
    @property
    def aliases(self) -> Set[str]:
        return {'ruby'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            PrefRecipe(
                src=Path('bundle/'),
                dst=xdglib.config('bundle/')
            ),
        ]


class NodeCookBook(CookBook):
    @property
    def aliases(self) -> Set[str]:
        return {'node'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            PrefRecipe(
                src=Path('npm/'),
                dst=xdglib.config('npm/')
            ),
        ]

    def activate(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        hist = Path('~/.local/share/node/history').expanduser()

        if not hist.parent.is_dir():
            self._mkdir(hist.parent, logger=logger, noop=noop)

        self._touch(hist, logger=logger, noop=noop)


class XcodeCookBook(CookBook):
    @property
    def aliases(self) -> Set[str]:
        return {'xcode'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='cask/Xcode/',
                dst='~/Library/Developer/Xcode',
            )
        ]

    @property
    def private(self) -> bool:
        return True


class IntelliJIdeaCookBook(CookBook):
    @property
    def aliases(self) -> Set[str]:
        return {'intellij'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='cask/IntelliJIdea/',
                dst='~/Library/Preferences/IntelliJIdea*',
            ),
            *PrefRecipe.glob(
                src='cask/IntelliJIdea/',
                dst='~/Library/ApplicationSupport/JetBrains/IntelliJIdea*',
            ),
        ]

    @property
    def private(self) -> bool:
        return True


class AndroidStudioCookBook(CookBook):
    @property
    def aliases(self) -> Set[str]:
        return {'android-studio'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='cask/AndroidStudio/',
                dst='~/Library/Preferences/AndroidStudio*',
            ),
            *PrefRecipe.glob(
                src='cask/AndroidStudio/',
                dst='~/Library/ApplicationSupport/Google/AndroidStudio*',
            ),
        ]

    @property
    def private(self) -> bool:
        return True


class AppCodeCookBook(CookBook):
    @property
    def aliases(self) -> Set[str]:
        return {'appcode'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='cask/AppCode/',
                dst='~/Library/Preferences/AppCode*',
            ),
            *PrefRecipe.glob(
                src='cask/AppCode/',
                dst='~/Library/ApplicationSupport/JetBrains/AppCode*',
            ),
        ]

    @property
    def private(self) -> bool:
        return True


class RubyMineCookBook(CookBook):
    @property
    def aliases(self) -> Set[str]:
        return {'rubymine'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='cask/RubyMine/',
                dst='~/Library/Preferences/RubyMine*',
            ),
            *PrefRecipe.glob(
                src='cask/RubyMine/',
                dst='~/Library/ApplicationSupport/JetBrains/RubyMine*',
            ),
        ]

    @property
    def private(self) -> bool:
        return True


class GoLandCookBook(CookBook):
    @property
    def aliases(self) -> Set[str]:
        return {'goland'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='cask/GoLand/',
                dst='~/Library/Preferences/GoLand*',
            ),
            *PrefRecipe.glob(
                src='cask/GoLand/',
                dst='~/Library/ApplicationSupport/JetBrains/GoLand*',
            ),
        ]

    @property
    def private(self) -> bool:
        return True


class CLionCookBook(CookBook):
    @property
    def aliases(self) -> Set[str]:
        return {'clion'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='cask/CLion/',
                dst='~/Library/Preferences/CLion*',
            ),
            *PrefRecipe.glob(
                src='cask/CLion/',
                dst='~/Library/ApplicationSupport/JetBrains/CLion*',
            ),
        ]

    @property
    def private(self) -> bool:
        return True


class RiderCookBook(CookBook):
    @property
    def aliases(self) -> Set[str]:
        return {'rider'}

    @property
    def prefs(self) -> List[PrefRecipe]:
        return [
            *PrefRecipe.glob(
                src='cask/Rider/',
                dst='~/Library/Preferences/Rider*',
            ),
            *PrefRecipe.glob(
                src='cask/Rider/',
                dst='~/Library/ApplicationSupport/JetBrains/Rider*',
            ),
        ]

    @property
    def private(self) -> bool:
        return True
