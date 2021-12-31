import subprocess
from enum import Enum
from pathlib import Path
from subprocess import CompletedProcess
from typing import Optional, Union, List

from .timber import Lumber

__all__ = [
    'Identity', 'Shell'
]


class Identity(Enum):
    UBUNTU = "ubuntu"
    DEBIAN = "debian"
    CENTOS = "centos"
    AMAZON = "amazon"
    DARWIN = "darwin"
    DEFAULT = "default"

    def is_linux(self) -> bool:
        return self in [Identity.UBUNTU, Identity.DEBIAN, Identity.CENTOS, Identity.AMAZON]

    def is_darwin(self) -> bool:
        return self in [Identity.DARWIN]

    def is_windows(self) -> bool:
        return self in []

    @classmethod
    def detect(cls) -> 'Identity':
        issue = Path("/etc/issue")

        if issue.is_file():
            name = issue.read_text().lower()
        else:
            output = subprocess.check_output(["uname", "-a"])
            name = output.decode('utf-8').strip().lower()

        if "ubuntu" in name:
            return Identity.UBUNTU

        if "debian" in name:
            return Identity.DEBIAN

        if "centos" in name:
            return Identity.CENTOS

        if "amzn" in name:
            return Identity.AMAZON

        if "darwin" in name:
            return Identity.DARWIN

        return Identity.DEFAULT


class Shell:
    logger: Lumber
    noop: bool

    def __init__(self, logger: Lumber = Lumber.noop(), noop: bool = False):
        self.noop = noop
        self.logger = logger
        return

    @classmethod
    def available(cls, command: str) -> bool:
        code = subprocess.call(
            ["which", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return code == 0

    def execute(self, command: Union[List[str], str]) -> bool:
        if isinstance(command, list):
            args = command
        elif isinstance(command, str):
            args = command.split()
        else:
            args = []

        if not args:
            return False

        self.logger.execute(" ".join(args))

        if self.noop:
            return True

        return subprocess.call(args) == 0

    def capture(self, command: Union[List[str], str]) -> Optional[CompletedProcess]:
        if isinstance(command, list):
            args = command
        elif isinstance(command, str):
            args = command.split()
        else:
            args = []

        if not args:
            return None

        if self.noop:
            return None

        return subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
