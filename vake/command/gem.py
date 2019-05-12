# 1st
import os
import re

# 2nd
from .. import osx
from . import base

GEM = "gem"
GEMFILE = "Gemfile"


class GemAction(base.Action):
    def gems(self):
        path = os.path.join(os.getcwd(), osx.sysname(), GEMFILE)

        if self.logger:
            self.logger.debug("Read gems from file: %s" % path)

        if os.path.exists(path):
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
            self.shell.execute([
                GEM, "install", gem.name, "--version", gem.version
            ])

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
        if not os.path.exists(path):
            return []

        gems = []

        # filter lines like following:
        #   gem 'awesome_gem1', '~> 1.2.3'
        #   gem "awesome_gem2", "~> 1.2.3"
        #   gem "awesome_gem3"

        pattern = re.compile(
            r"^\s*gem\s+[\"'](?P<name>\w+)[\"']\s*(,\s*[\"'](?P<version>.+)[\"'])?"
        )

        for line in open(path).read().splitlines():
            match = pattern.search(line)

            if match:
                n = match.group("name")
                v = match.group("version")
                gems.append(Gem(n, v))

        return gems
