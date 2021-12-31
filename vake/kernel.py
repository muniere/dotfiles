import subprocess
from enum import Enum
from pathlib import Path

__all__ = [
    'Identity'
]


def identify() -> 'Identity':
    issue = Path('/etc/issue')

    if issue.is_file():
        name = issue.read_text().lower()
    else:
        output = subprocess.check_output(['uname', '-a'])
        name = output.decode('utf-8').strip().lower()

    if 'ubuntu' in name:
        return Identity.UBUNTU

    if 'debian' in name:
        return Identity.DEBIAN

    if 'centos' in name:
        return Identity.CENTOS

    if 'amzn' in name:
        return Identity.AMAZON

    if 'darwin' in name:
        return Identity.DARWIN

    return Identity.DEFAULT


class Identity(Enum):
    UBUNTU = 'ubuntu'
    DEBIAN = 'debian'
    CENTOS = 'centos'
    AMAZON = 'amazon'
    DARWIN = 'darwin'
    DEFAULT = 'default'

    def is_linux(self) -> bool:
        return self in [Identity.UBUNTU, Identity.DEBIAN, Identity.CENTOS, Identity.AMAZON]

    def is_darwin(self) -> bool:
        return self in [Identity.DARWIN]

    def is_windows(self) -> bool:
        return self in []
