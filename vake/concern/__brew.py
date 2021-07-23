# 1st
import os

# 2nd
from .. import filetree
from .. import kernel
from . import __base__

BREW = "brew"
BREWFILE = "Brewfile"


class BrewAction(__base__.Action):
    def load_kegs(self):
        src = filetree.pilot(os.getcwd()).append(kernel.sysname()).append(BREWFILE)

        if self.logger:
            self.logger.debug("Read kegs from file: %s" % src)

        if src.exists():
            return Keg.load(src)
        else:
            return []

    def list_kegs(self):
        stdout = self.shell.capture([BREW, "list"]).stdout
        return [Keg(name) for name in stdout.decode('utf8').strip().splitlines()]


class InstallAction(BrewAction):
    def run(self):
        if not self.shell.available(BREW):
            self.logger.warn("Command is not available: %s" % BREW)
            return

        kegs = self.load_kegs()

        if not kegs:
            self.logger.info("No available kegs were found")
            return

        found = set(self.list_kegs())

        for keg in kegs:
            if keg in found:
                self.logger.info("%s is already installed" % keg.name)
            else:
                self.shell.execute([BREW, "install", keg.name])

        return


class UninstallAction(BrewAction):
    def run(self):
        if not self.shell.available(BREW):
            self.logger.warn("Command is not available: %s" % BREW)
            return

        kegs = self.load_kegs()

        if not kegs:
            self.logger.info("No available kegs were found")
            return

        found = set(self.list_kegs())

        for keg in found:
            if keg in found:
                self.shell.execute([BREW, "uninstall", keg.name])
            else:
                self.logger.info("%s is not installed" % keg.name)

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

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and self.name == o.name

    def __hash__(self) -> int:
        return hash(self.name)

    @staticmethod
    def load(path):
        target = filetree.pilot(path)

        if not target.exists():
            return []

        kegs = []

        for name in target.readlines():
            kegs.append(Keg(name))

        return kegs
