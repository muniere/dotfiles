# 2nd
from .. import xos
from ..xos import xpath

# 3rd
import base

CASK = "brew-cask"
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
        if not self.shell.available(CASK):
            self.logger.warn("Command is not available: %s" % CASK)
            return

        casks = self.casks()

        if not casks:
            self.logger.info("No available casks were found")
            return

        for cask in casks:
            self.shell.execute([CASK, "install", cask])

        return


class Uninstall(CaskAction):
    def run(self):
        if not self.shell.available(CASK):
            self.logger.warn("Command is not available: %s" % CASK)
            return

        casks = self.casks()

        if not casks:
            self.logger.info("No available casks were found")
            return

        for cask in casks:
            self.shell.execute([CASK, "uninstall", cask])

        return


class Status(CaskAction):
    def run(self):
        if not self.shell.available(CASK):
            self.logger.warn("Command is not available: %s" % CASK)
            return

        self.shell.execute([CASK, "list"])
        return
