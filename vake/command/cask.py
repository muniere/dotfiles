# 2nd
from .. import xos
from ..xos import xpath

# 3rd
import base

BREW = "brew"
CASK = "cask"
CASKFILE = "Caskfile"


class CaskAction(base.Action):
    def casks(self):
        path = xpath.join(xos.getcwd(), xos.sysname(), CASKFILE)

        if self.logger:
            self.logger.debug("Read casks from file: %s" % path)

        if xpath.exists(path):
            return open(path).read().splitlines()
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
            self.shell.execute([BREW, CASK, "install", cask])

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
            self.shell.execute([BREW, CASK, "uninstall", cask])

        return


class Status(CaskAction):
    def run(self):
        if not self.shell.available(BREW):
            self.logger.warn("Command is not available: %s" % BREW)
            return

        self.shell.execute([BREW, CASK, "list"])
        return
