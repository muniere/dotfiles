# 1st
import os
import json

# 2nd
from .. import osx
from . import base

NPM = "npm"
PACKAGE_JSON = "package.json"
DEPENDENCIES = "dependencies"


class NpmAction(base.Action):
    def packages(self):
        path = os.path.join(os.getcwd(), osx.sysname(), PACKAGE_JSON)

        if self.logger:
            self.logger.debug("Read packages from file: %s" % path)

        if os.path.exists(path):
            return Package.load(path)
        else:
            return []


class Install(NpmAction):
    def run(self):
        if not self.shell.available(NPM):
            self.logger.warn("Command is not available: %s" % NPM)
            return

        packages = self.packages()

        if not packages:
            self.logger.info("No available packages were found")
            return

        for package in packages:
            self.shell.execute([NPM, "install", "--global", "%s@%s" % (package.name, package.version)])

        return


class Uninstall(NpmAction):
    def run(self):
        if not self.shell.available(NPM):
            self.logger.warn("Command is not available: %s" % NPM)
            return

        packages = self.packages()

        if not packages:
            self.logger.info("No available gems were found")
            return

        for package in packages:
            self.shell.execute([NPM, "uninstall", "--global", package.name])

        return


class Status(NpmAction):
    def run(self):
        if not self.shell.available(NPM):
            self.logger.warn("Command is not available: %s" % NPM)
            return

        self.shell.execute([NPM, "list", "--global", "--depth=0"])
        return


class Package:
    def __init__(self, name, version):
        self.name = name
        self.version = version
        return

    @staticmethod
    def load(path):
        if not os.path.exists(path):
            return []

        dictionary = json.load(open(path))

        if not DEPENDENCIES in dictionary:
            return []

        packages = []

        for n, v in dictionary[DEPENDENCIES].items():
            packages.append(Package(name=n, version=v))

        return packages
