# 1st
import os

# 2nd
from .. import filetree
from .. import kernel
from . import __base__

BREW = "brew"
BREWFILE = "Brewfile"


class BrewAction(__base__.Action):
    def kegs(self):
        src = filetree.pilot(os.getcwd()).append(kernel.sysname()).append(BREWFILE)

        if self.logger:
            self.logger.debug("Read kegs from file: %s" % src)

        if src.exists():
            return Keg.load(src)
        else:
            return []


class InstallAction(BrewAction):
    def run(self):
        if not self.shell.available(BREW):
            self.logger.warn("Command is not available: %s" % BREW)
            return

        kegs = self.kegs()

        if not kegs:
            self.logger.info("No available kegs were found")
            return

        for keg in kegs:
            self.shell.execute([BREW, "install", keg.name])

        return


class UninstallAction(BrewAction):
    def run(self):
        if not self.shell.available(BREW):
            self.logger.warn("Command is not available: %s" % BREW)
            return

        kegs = self.kegs()

        if not kegs:
            self.logger.info("No available kegs were found")
            return

        for keg in kegs:
            self.shell.execute([BREW, "uninstall", keg.name])

        return


class StatusAction(BrewAction):
    def run(self):
        if not self.shell.available(BREW):
            self.logger.warn("Command is not available: %s" % BREW)
            return

        self.shell.execute([BREW, "tap"])
        self.shell.execute([BREW, "list"])
        return


class Keg:
    def __init__(self, name):
        self.name = name
        return

    @staticmethod
    def load(path):
        target = filetree.pilot(path)

        if not target.exists():
            return []

        kegs = []

        for name in target.readlines():
            kegs.append(Keg(name))

        return kegs
