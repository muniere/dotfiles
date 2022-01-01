import subprocess

from vake.timber import Lumber


def ensure(command: str):
    assert available(command), f'command not available: {command}'


def available(command: str) -> bool:
    code = subprocess.call(
        ['which', command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return code == 0


def execute(args: list[str], logger: Lumber = Lumber.noop(), noop: bool = False) -> bool:
    assert len(args) > 0, 'args must not be empty'

    logger.execute(' '.join(args))

    if noop:
        return True

    return subprocess.call(args) == 0


def capture(args: list[str]) -> subprocess.CompletedProcess:
    assert len(args) > 0, 'args must not be empty'

    return subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True
    )
