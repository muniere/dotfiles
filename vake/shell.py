import os
import subprocess
import sys
import time
from typing import Optional, Dict

from . import _
from .timber import Lumber
from .tty import Looper

__all__ = [
    'SubprocessError', 'which', 'call', 'run'
]

SubprocessError = subprocess.SubprocessError


def call(
    cmd: str,
    env: Optional[Dict[str, str]] = None,
    logger: Lumber = Lumber.noop(),
    noop: bool = False,
) -> int:
    assert len(cmd) > 0, 'cmd must not be empty'

    environ = _.safe(env, {})

    words = [f'{k}={v}' for (k, v) in environ.items()] + [cmd]
    logger.trace(' '.join(words))

    if noop:
        return True

    return subprocess.call(cmd, env={**os.environ.copy(), **environ}, shell=True)


def poll(
    cmd: str,
    env: Optional[Dict[str, str]] = None,
    eol: Optional[Looper] = None,
    fps: int = 10,
) -> subprocess.CompletedProcess:
    assert len(cmd) > 0, 'cmd must not be empty'

    environ = _.safe(env, {})

    with subprocess.Popen(cmd, env=environ, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True) as popen:
        looper = _.safe(eol, Looper.dots())

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
    env: Optional[Dict[str, str]] = None,
    check: bool = False,
) -> subprocess.CompletedProcess:
    assert len(cmd) > 0, 'cmd must not be empty'

    environ = _.safe(env, {})

    return subprocess.run(cmd, env=environ, capture_output=True, check=check, shell=True)


def which(command: str) -> subprocess.CompletedProcess:
    return subprocess.run(f'which {command}', capture_output=True, check=True, shell=True)
