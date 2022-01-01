import subprocess

from .timber import Lumber


def which(command: str) -> subprocess.CompletedProcess:
    return subprocess.run(['which', command], capture_output=True, check=True)


def call(args: list[str], logger: Lumber = Lumber.noop(), noop: bool = False) -> int:
    assert len(args) > 0, 'args must not be empty'

    logger.execute(' '.join(args))

    if noop:
        return True

    return subprocess.call(args)


def run(args: list[str]) -> subprocess.CompletedProcess:
    assert len(args) > 0, 'args must not be empty'

    return subprocess.run(args, capture_output=True, check=True)
