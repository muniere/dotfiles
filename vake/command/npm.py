# 1st
import os
import json

# 2nd
from .. import fs
from .. import osx
from . import base

NPM = "npm"
PACKAGE_JSON = "package.json"
DEPENDENCIES = "dependencies"


class NpmAction(base.Action):
    def packages(self):
        src = fs.pilot(os.getcwd()).append(osx.sysname()).append(PACKAGE_JSON)

        if self.logger:
            self.logger.debug("Read packages from file: %s" % src)

        if src.exists():
            return Package.load(src)
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
            spec = "%s@%s" % (package.name, package.version)
            self.shell.execute([NPM, "install", "--global", spec])

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
        target = fs.pilot(path)

        if not target.exists():
            return []

        content = target.read()
        jsonobj = json.loads(content)

        if not DEPENDENCIES in jsonobj:
            return []

        packages = []

        for name, version in jsonobj[DEPENDENCIES].items():
            packages.append(Package(name, version))

        return packages
