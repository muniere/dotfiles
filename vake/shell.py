import os
import subprocess
import sys
import time
from typing import Optional

from .timber import Lumber
from .tty import Looper

__all__ = [
    'SubprocessError', 'which', 'call', 'run'
]

SubprocessError = subprocess.SubprocessError


def call(
    cmd: str,
    env: Optional[dict[str, str]] = None,
    logger: Lumber = Lumber.noop(),
    noop: bool = False,
) -> int:
    assert len(cmd) > 0, 'cmd must not be empty'

    if env:
        words = [f'{k}={v}' for (k, v) in env.items()] + [cmd]
        env_vars = os.environ.copy().update(env)
    else:
        words = [cmd]
        env_vars = None

    logger.trace(' '.join(words))

    if noop:
        return True

    return subprocess.call(cmd, env=env_vars, shell=True)


def poll(
    cmd: str,
    env: Optional[dict[str, str]] = None,
    eol: Optional[Looper] = None,
    fps: int = 10,
) -> subprocess.CompletedProcess:
    assert len(cmd) > 0, 'cmd must not be empty'

    if env:
        env_vars = os.environ.copy().update(env)
    else:
        env_vars = None

    with subprocess.Popen(cmd, env=env_vars, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True) as popen:
        looper = eol or Looper.dots()

        while True:
            ret = popen.poll()

            if ret is None:
                text = next(looper)
                sys.stdout.write(text)
                sys.stdout.flush()
                time.sleep(1.0 / fps)
                sys.stdout.write('\b' * len(text))
            else:
                sys.stdout.write('\r')
                return subprocess.CompletedProcess(
                    args=cmd,
                    returncode=ret,
                    stdout=popen.stdout,
                    stderr=popen.stderr,
                )


def run(
    cmd: str,
    env: Optional[dict[str, str]] = None,
    check: bool = False,
) -> subprocess.CompletedProcess:
    assert len(cmd) > 0, 'cmd must not be empty'

    if env:
        env_vars = os.environ.copy().update(env)
    else:
        env_vars = None

    return subprocess.run(cmd, env=env_vars, capture_output=True, check=check, shell=True)


def which(command: str) -> subprocess.CompletedProcess:
    return subprocess.run(f'which {command}', capture_output=True, check=True, shell=True)
