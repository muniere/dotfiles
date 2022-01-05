import os
import subprocess
from typing import Optional

from .timber import Lumber

__all__ = [
    'SubprocessError', 'which', 'call', 'run'
]

SubprocessError = subprocess.SubprocessError


def which(command: str) -> subprocess.CompletedProcess:
    return subprocess.run(['which', command], capture_output=True, check=True)


def call(
    args: list[str],
    env: Optional[dict[str, str]] = None,
    logger: Lumber = Lumber.noop(),
    noop: bool = False,
) -> int:
    assert len(args) > 0, 'args must not be empty'

    if env:
        words = [f'{k}={v}' for (k, v) in env.items()] + args
        env_vars = os.environ.copy().update(env)
    else:
        words = args
        env_vars = None

    logger.execute(' '.join(words))

    if noop:
        return True

    return subprocess.call(args, env=env_vars)


def run(
    args: list[str],
    env: Optional[dict[str, str]] = None,
    check: bool = False,
) -> subprocess.CompletedProcess:
    assert len(args) > 0, 'args must not be empty'

    if env:
        env_vars = os.environ.copy().update(env)
    else:
        env_vars = None

    return subprocess.run(args, env=env_vars, capture_output=True, check=check)


def popen(
    args: list[str],
    env: Optional[dict[str, str]] = None,
) -> subprocess.Popen:
    assert len(args) > 0, 'args must not be empty'

    if env:
        env_vars = os.environ.copy().update(env)
    else:
        env_vars = None

    return subprocess.Popen(args, env=env_vars, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class Sequencer:
    __seq: list[str]
    __i: int

    def __init__(self, seq: list[str]):
        self.__seq = seq
        self.__i = 0

    def __next__(self):
        char = self.__seq[self.__i]
        self.__i = (self.__i + 1) % len(self.__seq)
        return char

    def __iter__(self):
        return self
