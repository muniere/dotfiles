"""
Package of shell commands
"""

# 1st
import subprocess

# 2nd
from .. import filetree


def shell(noop=False, logger=None):
    return Shell(noop, logger)


class Shell:
    def __init__(self, noop=False, logger=None):
        self.noop = noop
        self.logger = logger
        return

    @classmethod
    def available(cls, command) -> bool:
        code = subprocess.call(["which", command],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        return code == 0

    def mkdir(self, path, recursive=False) -> bool:
        words = ["mkdir"]

        if recursive:
            words.append("-p")

        words.append(path)

        return self.execute(words)

    def remove(self, path, recursive=False, force=False) -> bool:
        words = ["rm"]

        if recursive:
            words.append("-r")

        if force:
            words.append("-f")

        words.append(path)

        return self.execute(words)

    def symlink(self, src, dst, force=False) -> bool:
        words = ["ln", "-s"]

        if force:
            words.append("-f")

        words.append(src)
        words.append(dst)

        return self.execute(words)

    def git_clone(self, src, dst) -> bool:
        if filetree.pilot(dst).isdir():
            if self.logger:
                self.logger.info("Worktree already exists: %s" % dst)
            return True

        return self.execute(["git", "clone", "--recursive", src, dst])

    def execute(self, command) -> bool:
        if isinstance(command, list):
            words = command
        elif isinstance(command, str):
            words = command.split()
        else:
            words = []

        if not words:
            return

        if self.logger:
            self.logger.execute("%s" % " ".join(words))

        if self.noop:
            return True

        return subprocess.call(words) == 0

    def capture(self, command) -> subprocess.CompletedProcess:
        if isinstance(command, list):
            words = command
        elif isinstance(command, str):
            words = command.split()
        else:
            words = []

        if not words:
            return

        if self.noop:
            return None

        return subprocess.run(words, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
