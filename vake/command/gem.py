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

        # filter lines like following:
        #   gem 'awesome_gem1', '~> 1.2.3'
        #   gem "awesome_gem2", "~> 1.2.3"
        #   gem "awesome_gem3"

        for line in open(path).read().splitlines():

            match = re.compile("^\s*gem\s+[\"'](?P<name>\w+)[\"']\s*(,\s*[\"'](?P<version>.+)[\"'])?").search(line)

            if match:
                gems.append(Gem(name=match.group("name"), version=match.group("version")))

        return gems
