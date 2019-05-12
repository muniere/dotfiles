# 1st
import os
import glob
import re

# 2nd
from .. import fs
from .. import osx
from . import base


class BinfileAction(base.Action):
    def binfiles(self):
        return [
            Binfile(src="bin", dst="~/.bin")
        ]


class Install(BinfileAction):
    def run(self):
        for binfile in self.binfiles():
            self.__run(binfile, sysname=osx.sysname())
            self.__run(binfile, sysname="default")

        return

    def __run(self, binfile, sysname="default"):
        if not self.__istarget(binfile):
            if self.logger:
                relpath = fs.pilot(binfile.src).relpath(os.getcwd())
                self.logger.info("File is not target: %s" % relpath)
            return

        src = fs.pilot(binfile.src).prepend(sysname).abspath()
        dst = fs.pilot(binfile.dst).expanduser()

        #
        # guard
        #

        # src not found
        if not src.exists():
            return False

        # dst link already exists
        if dst.islink():
            if self.logger:
                self.logger.info("Symlink already exists: %s" % dst.reduceuser())
            return False

        #
        # file
        #
        if src.isfile():
            # another file already exists
            if dst.isfile():
                if self.logger:
                    self.logger.info("File already exists: %s" % dst.reduceuser())
                return False

            # ensure parent directory
            dst_dir = dst.parent()
            if not dst_dir.isdir():
                self.shell.mkdir(dst_dir.pathname(), recursive=True)

            # create symbolic link
            return self.shell.symlink(src.pathname(), dst.pathname(), force=True)

        #
        # directory
        #
        if src.isdir():
            for new_src in src.children(target='f', recursive=True):
                new_dst = fs.pilot(binfile.dst).append(new_src.relpath(src))
                new_bin = Binfile(src=new_src.pathname(), dst=new_dst.pathname())
                self.__run(new_bin, sysname=sysname)

        return True

    def __istarget(self, binfile):
        blacklist = [r'\.swp$']

        for pattern in blacklist:
            if re.search(pattern, binfile.src):
                return False

        return True


class Uninstall(BinfileAction):
    def run(self):
        for binfile in self.binfiles():
            self.__run(binfile, sysname=osx.sysname())
            self.__run(binfile, sysname="default")

        return

    def __run(self, binfile, sysname="default"):
        if not self.__istarget(binfile):
            if self.logger:
                relpath = fs.pilot(binfile.src).relpath(os.getcwd())
                self.logger.info("File is not target: %s" % relpath)
            return

        src = fs.pilot(binfile.src).prepend(sysname).abspath()
        dst = fs.pilot(binfile.dst).expanduser()

        #
        # guard
        #

        # src not found
        if not src.exists():
            return True

        # dst not found
        if not dst.exists() and not dst.islink():
            if self.logger:
                self.logger.info("File already removed: %s" % dst)
            return True

        #
        # symlink
        #
        if dst.islink():
            return self.shell.remove(dst.pathname())

        #
        # file
        #
        if dst.isfile():
            if self.logger:
                self.logger.info("File is not symlink: %s" % dst)
            return False

        #
        # directory
        #
        if src.isdir():
            for new_src in src.children(target='f', recursive=True):
                new_dst = fs.pilot(binfile.dst).append(new_src.relpath(src))
                new_bin = Binfile(src=new_src.pathname(), dst=new_dst.pathname())
                self.__run(new_bin, sysname=sysname)

        return True

    def __istarget(self, binfile):
        blacklist = [r'\.swp$']

        for pattern in blacklist:
            if re.search(pattern, binfile.src):
                return False

        return True


class Status(BinfileAction):
    def run(self):
        binfiles = sorted(self.binfiles(), key=lambda x: x.dst)

        for binfile in binfiles:
            target = fs.pilot(binfile.dst).expanduser()

            if not target.exists():
                continue

            if osx.isdarwin():
                self.shell.execute("ls -lFG %s" % target)
            else:
                self.shell.execute("ls -lFo %s" % target)

        return True


class Binfile:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst
        return
