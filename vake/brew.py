import subprocess
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
    try:
        shell.which('brew')
    except subprocess.CalledProcessError as err:
        raise AssertionError('command not available: brew') from err


def load_list() -> list[Keg]:
    identity = kernel.identify()
    src = Path(locate.static(), identity.value, 'Brewfile').resolve()

    if not src.exists():
        return []

    lines = src.read_text(encoding='utf-8').splitlines()
    return [Keg(name) for name in lines]


def run_list() -> list[Keg]:
    stdout = shell.run(['brew', 'list']).stdout
    lines = stdout.decode('utf-8').strip().splitlines()
    return [Keg(name) for name in lines]


def call_install(keg: Keg, logger: Lumber = Lumber.noop(), noop: bool = False):
    shell.call(['brew', 'install', keg.name], logger=logger, noop=noop)


def call_uninstall(keg: Keg, logger: Lumber = Lumber.noop(), noop: bool = False):
    shell.call(['brew', 'uninstall', keg.name], logger=logger, noop=noop)


def call_list(logger: Lumber = Lumber.noop(), noop: bool = False):
    shell.call(['brew', 'list'], logger=logger, noop=noop)


def call_tap(logger: Lumber = Lumber.noop(), noop: bool = False):
    shell.call(['brew', 'tap'], logger=logger, noop=noop)
