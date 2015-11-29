# 1st
import re

# 2nd
from .. import xos
from ..xos import xpath

# 3rd
import base

GEM = "gem"
GEMFILE = "Gemfile"


class GemAction(base.Action):
    def gems(self):
        path = xpath.join(xos.getcwd(), xos.sysname(), GEMFILE)

        if self.logger:
            self.logger.debug("Read gems from file: %s" % path)

        if xpath.exists(path):
            return Gem.load(path)
        else:
            return []


class Install(GemAction):
    def run(self):
        if not self.shell.available(GEM):
            self.logger.warn("Command is not available: %s" % GEM)
            return

        gems = self.gems()

        if not gems:
            self.logger.info("No available gems were found")
            return

        for gem in gems:
            self.shell.execute([GEM, "install", gem.name, "--version", gem.version])

        return


class Uninstall(GemAction):
    def run(self):
        if not self.shell.available(GEM):
            self.logger.warn("Command is not available: %s" % GEM)
            return

        gems = self.gems()

        if not gems:
            self.logger.info("No available gems were found")
            return

        for gem in gems:
            self.shell.execute([GEM, "uninstall", gem.name])

        return


class Status(GemAction):
    def run(self):
        if not self.shell.available(GEM):
            self.logger.warn("Command is not available: %s" % GEM)
            return

        self.shell.execute([GEM, "list"])
        return


class Gem:
    def __init__(self, name, version):
        self.name = name
        self.version = version
        return

    @staticmethod
    def load(path):
        if not xpath.exists(path):
            return []

        gems = []

        for line in filter(lambda l: re.match("^gem", l), open(path).read().splitlines()):
            n, v = map(lambda s: s.strip(), re.sub("^gem", "", line).strip().split(","))
            gems.append(Gem(name=n, version=v))

        return gems
