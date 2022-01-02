import os
import subprocess

from .timber import Lumber


def which(command: str) -> subprocess.CompletedProcess:
    return subprocess.run(['which', command], capture_output=True, check=True)


def call(
    args: list[str],
    env: dict[str, str] = None,
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
    env: dict[str, str] = None,
) -> subprocess.CompletedProcess:
    assert len(args) > 0, 'args must not be empty'

    if env:
        env_vars = os.environ.copy().update(env)
    else:
        env_vars = None

    return subprocess.run(args, env=env_vars, capture_output=True, check=True)
