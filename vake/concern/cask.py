# 1st
import os

# 2nd
from .. import filetree
from .. import kernel
from . import __base__

BREW = "brew"
CASK = "cask"
CASKFILE = "Caskfile"


class CaskAction(__base__.Action):
    def casks(self):
        src = filetree.pilot(os.getcwd()).append(kernel.sysname()).append(CASKFILE)

        if self.logger:
            self.logger.debug("Read casks from file: %s" % src)

        if src.exists():
            return Cask.load(src)
        else:
            return []


class Install(CaskAction):
    def run(self):
        if not self.shell.available(BREW):
            self.logger.warn("Command is not available: %s" % BREW)
            return

        casks = self.casks()

        if not casks:
            self.logger.info("No available casks were found")
            return

        for cask in casks:
            self.shell.execute([BREW, CASK, "install", cask.name])

        return


class Uninstall(CaskAction):
    def run(self):
        if not self.shell.available(BREW):
            self.logger.warn("Command is not available: %s" % BREW)
            return

        casks = self.casks()

        if not casks:
            self.logger.info("No available casks were found")
            return

        for cask in casks:
            self.shell.execute([BREW, CASK, "uninstall", cask.name])

        return


class Status(CaskAction):
    def run(self):
        if not self.shell.available(BREW):
            self.logger.warn("Command is not available: %s" % BREW)
            return

        self.shell.execute([BREW, CASK, "list"])
        return



class Cask:
    def __init__(self, name):
        self.name = name
        return

    @staticmethod
    def load(path):
        target = filetree.pilot(path)

        if not target.exists():
            return []

        casks = []

        for name in target.readlines():
            casks.append(Cask(name))

        return casks
