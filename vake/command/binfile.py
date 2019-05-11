# 1st
import os
import glob
import re

# 2nd
from .. import xos
from . import base

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
                self.logger.info("File is not target: %s" % os.path.relpath(binfile.src, os.getcwd()))
            return

        src = os.path.abspath(os.path.join(sysname, binfile.src))
        dst = os.path.expanduser(binfile.dst)

        #
        # guard
        #

        # src not found
        if not os.path.exists(src):
            return False

        # dst link already exists
        if os.path.islink(dst):
            if self.logger:
                self.logger.info("Symlink already exists: %s" % xos.xpath.reduceuser(dst))
            return False

        #
        # file
        #
        if os.path.isfile(src):
            # another file already exists
            if os.path.isfile(dst):
                if self.logger:
                    self.logger.info("File already exists: %s" % xos.xpath.reduceuser(dst))
                return False

            # ensure parent directory
            dst_dir = os.path.dirname(dst)
            if not os.path.isdir(dst_dir):
                self.shell.mkdir(dst_dir, recursive=True)

            # create symbolic link
            return self.shell.symlink(src, dst, force=True)

        #
        # directory
        #
        if os.path.isdir(src):
            for new_src in xos.listdir_f(src, recursive=True):
                rel_dst = os.path.relpath(new_src, src)
                new_dst = os.path.join(binfile.dst, rel_dst)
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
                self.logger.info("File is not target: %s" % os.path.relpath(binfile.src, os.getcwd()))
            return

        src = os.path.abspath(os.path.join(sysname, binfile.src))
        dst = os.path.expanduser(binfile.dst)

        #
        # guard
        #

        # src not found
        if not os.path.exists(src):
            return True

        # dst not found
        if not os.path.exists(dst) and not os.path.islink(dst):
            if self.logger:
                self.logger.info("File already removed: %s" % dst)
            return True

        #
        # symlink
        #
        if os.path.islink(dst):
            return self.shell.remove(dst)

        #
        # file
        #
        if os.path.isfile(dst):
            if self.logger:
                self.logger.info("File is not symlink: %s" % dst)
            return False

        #
        # directory
        #
        if os.path.isdir(src):
            for new_src in xos.listdir_f(src, recursive=True):
                rel_dst = os.path.relpath(new_src, src)
                new_dst = os.path.join(binfile.dst, rel_dst)
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

            target = os.path.expanduser(binfile.dst)

            if not os.path.exists(target):
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
