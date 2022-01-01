from dataclasses import dataclass
from pathlib import Path

from . import kernel
from . import locate
from . import shell
from .timber import Lumber


@dataclass(frozen=True)
class Keg:
    name: str


def ensure():
    shell.ensure('brew')


def load() -> list[Keg]:
    identity = kernel.identify()
    src = Path(locate.static(), identity.value, 'Brewfile').resolve()

    if not src.exists():
        return []

    lines = src.read_text().splitlines()
    return [Keg(name) for name in lines]


def capture() -> list[Keg]:
    stdout = shell.capture(['brew', 'list']).stdout
    lines = stdout.decode('utf8').strip().splitlines()
    return [Keg(name) for name in lines]


def install(keg: Keg, logger: Lumber = Lumber.noop(), noop: bool = False):
    shell.execute(['brew', 'install', keg.name], logger=logger, noop=noop)


def uninstall(keg: Keg, logger: Lumber = Lumber.noop(), noop: bool = False):
    shell.execute(['brew', 'uninstall', keg.name], logger=logger, noop=noop)


def list(logger: Lumber = Lumber.noop(), noop: bool = False):
    shell.execute(['brew', 'list'], logger=logger, noop=noop)


def tap(logger: Lumber = Lumber.noop(), noop: bool = False):
    shell.execute(['brew', 'tap'], logger=logger, noop=noop)
