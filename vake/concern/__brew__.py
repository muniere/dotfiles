# 1st
import os

from abc import ABCMeta
from dataclasses import dataclass
from typing import List

# 2nd
from .. import filetree
from .. import kernel
from . import __base__

BREW = "brew"
BREWFILE = "Brewfile"


@dataclass(eq=True, frozen=True)
class Keg:
    name: str


class BrewAction(__base__.Action, metaclass=ABCMeta):
    def load_kegs(self) -> List[Keg]:
        src = filetree.pilot(os.getcwd())\
            .append(kernel.sysname())\
            .append(BREWFILE)

        if self.logger:
            self.logger.debug("Read kegs from file: %s" % src)

        if not src.exists():
            return []

        lines = src.readlines()
        return [Keg(name) for name in lines]

    def list_kegs(self) -> List[Keg]:
        stdout = self.shell.capture([BREW, "list"]).stdout
        lines = stdout.decode('utf8').strip().splitlines()
        return [Keg(name) for name in lines]


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
