import subprocess
from typing import Optional, Union, List

from . import filetree
from . import winston

__all__ = [
    'islinux', 'isbsd', 'isdebian', 'isredhat', 'isdarwin', 'sysname', 'shell'
]

UBUNTU = "ubuntu"
DEBIAN = "debian"
CENTOS = "centos"
AMAZON = "amazon"
DARWIN = "darwin"


def islinux() -> bool:
    return sysname() in [UBUNTU, DEBIAN, CENTOS, AMAZON]


def isbsd() -> bool:
    return sysname() in [DARWIN]


def isdebian() -> bool:
    return sysname() in [UBUNTU, DEBIAN]


def isredhat() -> bool:
    return sysname() in [CENTOS, AMAZON]


def isdarwin() -> bool:
    return sysname() in [DARWIN]


def sysname() -> str:
    """
    Detect system name

    :return: Detected name
    """
    issue = filetree.pilot("/etc/issue")

    if issue.isfile():
        rawname = issue.read().lower()
    else:
        output = subprocess.check_output(["uname", "-a"])
        rawname = output.decode('utf-8').strip().lower()

    if "ubuntu" in rawname:
        return UBUNTU

    if "debian" in rawname:
        return DEBIAN

    if "centos" in rawname:
        return CENTOS

    if "amzn" in rawname:
        return AMAZON

    if "darwin" in rawname:
        return DARWIN

    return "default"


def shell(noop: bool = False, logger: Optional[winston.LoggerWrapper] = None) -> 'Shell':
    return Shell(noop, logger)


class Shell:
    noop: bool
    logger: Optional[winston.LoggerWrapper]

    def __init__(self, noop: bool = False, logger: Optional[winston.LoggerWrapper] = None):
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

    def mkdir(self, path: str, recursive: bool = False) -> bool:
        args = ["mkdir"]

        if recursive:
            args.append("-p")

        args.append(path)

        return self.execute(args)

    def remove(self, path: str, recursive: bool = False, force: bool = False) -> bool:
        args = ["rm"]

        if recursive:
            args.append("-r")

        if force:
            args.append("-f")

        args.append(path)

        return self.execute(args)

    def symlink(self, src: str, dst: str, force: bool = False) -> bool:
        args = ["ln", "-s"]

        if force:
            args.append("-f")

        args.append(src)
        args.append(dst)

        return self.execute(args)

    def execute(self, command: Union[List[str], str]) -> bool:
        if isinstance(command, list):
            args = command
        elif isinstance(command, str):
            args = command.split()
        else:
            args = []

        if not args:
            return False

        if self.logger:
            self.logger.execute("%s" % " ".join(args))

        if self.noop:
            return True

        return subprocess.call(args) == 0

    def capture(self, command: Union[List[str], str]) -> Optional[subprocess.CompletedProcess]:
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
