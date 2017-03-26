# 1st
import glob
import re

# 2nd
from .. import xos
from ..xos import xpath

# 3rd
import base

class BinfileAction(base.Action):
    def binfiles(self):
        return [
            Binfile(src="bin", dst="~/.bin")
        ]


class Install(BinfileAction):
    def run(self):
        for binfile in self.binfiles():
            self.__run(binfile, sysname=xos.sysname())
            self.__run(binfile, sysname="default")

        return

    def __run(self, binfile, sysname="default"):
        if not self.__istarget(binfile):
            if self.logger:
                self.logger.info("File is not target: %s" % xpath.relpath(binfile.src, xos.getcwd()))
            return

        src = xpath.abspath(xpath.join(sysname, binfile.src))
        dst = xpath.expanduser(binfile.dst)

        #
        # guard
        #

        # src not found
        if not xpath.exists(src):
            return False

        # dst link already exists
        if xpath.islink(dst):
            if self.logger:
                self.logger.info("Symlink already exists: %s" % xpath.reduceuser(dst))
            return False

        #
        # file
        #
        if xpath.isfile(src):
            # another file already exists
            if xpath.isfile(dst):
                if self.logger:
                    self.logger.info("File already exists: %s" % xpath.reduceuser(dst))
                return False

            # ensure parent directory
            dst_dir = xpath.dirname(dst)
            if not xpath.isdir(dst_dir):
                self.shell.mkdir(dst_dir, recursive=True)

            # create symbolic link
            return self.shell.symlink(src, dst, force=True)

        #
        # directory
        #
        if xpath.isdir(src):
            for new_src in xos.listdir_f(src, recursive=True):
                rel_dst = xpath.relpath(new_src, src)
                new_dst = xpath.join(binfile.dst, rel_dst)
                new_bin = Binfile(src=new_src, dst=new_dst)
                self.__run(new_bin, sysname=sysname)

        return True

    def __istarget(self, binfile):
        patterns = [
            '\.swp$'
        ]

        for pattern in patterns:
            if re.search(pattern, binfile.src):
                return False

        return True


class Uninstall(BinfileAction):
    def run(self):
        for binfile in self.binfiles():
            self.__run(binfile, sysname=xos.sysname())
            self.__run(binfile, sysname="default")

        return

    def __run(self, binfile, sysname="default"):
        if not self.__istarget(binfile):
            if self.logger:
                self.logger.info("File is not target: %s" % xpath.relpath(binfile.src, xos.getcwd()))
            return

        src = xpath.abspath(xpath.join(sysname, binfile.src))
        dst = xpath.expanduser(binfile.dst)

        #
        # guard
        #

        # src not found
        if not xpath.exists(src):
            return True

        # dst not found
        if not xpath.exists(dst) and not xpath.islink(dst):
            if self.logger:
                self.logger.info("File already removed: %s" % dst)
            return True

        #
        # symlink
        #
        if xpath.islink(dst):
            return self.shell.remove(dst)

        #
        # file
        #
        if xpath.isfile(dst):
            if self.logger:
                self.logger.info("File is not symlink: %s" % dst)
            return False

        #
        # directory
        #
        if xpath.isdir(src):
            for new_src in xos.listdir_f(src, recursive=True):
                rel_dst = xpath.relpath(new_src, src)
                new_dst = xpath.join(binfile.dst, rel_dst)
                new_bin = Binfile(src=new_src, dst=new_dst)
                self.__run(new_bin, sysname=sysname)

        return True

    def __istarget(self, binfile):
        patterns = [
            '\.swp$'
        ]

        for pattern in patterns:
            if re.search(pattern, binfile.src):
                return False

        return True

class Status(BinfileAction):
    def run(self):
        binfiles = sorted(self.binfiles(), key=lambda x: x.dst)

        for binfile in binfiles:

            target = xpath.expanduser(binfile.dst)

            if not xpath.exists(target):
                continue

            if xos.isdarwin():
                self.shell.execute("ls -lFG %s" % target)
            else:
                self.shell.execute("ls -lFo %s" % target)

        return True


class Binfile:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst
        return
