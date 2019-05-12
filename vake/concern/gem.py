# 1st
import os
import re

# 2nd
from .. import filetree
from .. import kernel
from . import __base__

GEM = "gem"
GEMFILE = "Gemfile"


class GemAction(__base__.Action):
    def gems(self):
        src = filetree.pilot(os.getcwd()).append(kernel.sysname()).append(GEMFILE)

        if self.logger:
            self.logger.debug("Read gems from file: %s" % src)

        if src.exists():
            return Gem.load(src)
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
        target = filetree.pilot(path)

        if not target.exists():
            return []

        pattern = re.compile(
            r"^\s*gem\s+[\"'](?P<name>\w+)[\"']\s*(,\s*[\"'](?P<version>.+)[\"'])?"
        )

        gems = []

        for line in target.readlines():
            match = pattern.search(line)

            if not match:
                continue

            name = match.group("name")
            version = match.group("version")
            gems.append(Gem(name, version))

        return gems
