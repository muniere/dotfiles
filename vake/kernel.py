import subprocess
from enum import Enum
from pathlib import Path

__all__ = [
    'Identity', 'identify'
]


class Identity(Enum):
    UBUNTU = 'ubuntu'
    DARWIN = 'darwin'
    DEFAULT = 'default'

    def is_linux(self) -> bool:
        return self in [Identity.UBUNTU]

    def is_darwin(self) -> bool:
        return self in [Identity.DARWIN]

    def is_windows(self) -> bool:
        return self in []


def identify() -> Identity:
    issue = Path('/etc/issue')

    if issue.is_file():
        name = issue.read_text(encoding='utf-8').lower()
    else:
        output = subprocess.check_output(['uname', '-a'])
        name = output.decode('utf-8').strip().lower()

    if 'ubuntu' in name:
        return Identity.UBUNTU

    if 'darwin' in name:
        return Identity.DARWIN

    return Identity.DEFAULT
