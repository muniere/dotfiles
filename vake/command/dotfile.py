# 1st
import os
import glob
import re

# 2nd
from .. import xos
from . import base

TEMPLATE_DIR = "./vake/template"


class DotfileAction(base.Action):
    def __vim_install(self):
        self.shell.git_clone(
            src="https://github.com/Shougo/neobundle.vim",
            dst=os.path.expanduser("~/.vim/bundle/neobundle.vim")
        )
        return None

    def __vim_uninstall(self):
        return None

    def dotfiles(self):
        dots = []

        # shared
        dots.extend([
            Dotfile(src="sh.d", dst="~/.sh.d"),

            Dotfile(src="bash.d", dst="~/.bash.d"),
            Dotfile(src="bash_completion.d", dst="~/.bash_completion.d"),

            Dotfile(src="zsh.d", dst="~/.zsh.d"),
            Dotfile(src="zsh-completions", dst="~/.zsh-completions"),
            Dotfile(src="/usr/local/library/Contributions/brew_zsh_completion.zsh", dst="~/.zsh-completions/_brew"),

            Dotfile(src="tmux.conf", dst="~/.tmux.conf"),
            Dotfile(src="gitconfig", dst="~/.gitconfig"),
            Dotfile(src="tigrc", dst="~/.tigrc"),
            Dotfile(src="peco", dst="~/.peco"),

            Dotfile(src="vimrc", dst="~/.vimrc"),
            Dotfile(src="vim", dst="~/.vim", install=self.__vim_install, uninstall=self.__vim_uninstall),

            Dotfile(src="gradle", dst="~/.gradle"),
        ])

        # linux
        if xos.islinux():
            dots.extend([])

        # darwin
        if xos.isdarwin():
            dots.extend(
                map(lambda dst: Dotfile(src="Xcode", dst=dst),
                    glob.glob(os.path.expanduser("~/Library/Developer/Xcode"))))

            dots.extend(
                map(lambda dst: Dotfile(src="IntelliJIdea", dst=dst),
                    glob.glob(os.path.expanduser("~/Library/Preferences/IntelliJIdea*"))))

            dots.extend(
                map(lambda dst: Dotfile(src="AndroidStudio", dst=dst),
                    glob.glob(os.path.expanduser("~/Library/Preferences/AndroidStudio*"))))

            dots.extend(
                map(lambda dst: Dotfile(src="AppCode", dst=dst),
                    glob.glob(os.path.expanduser("~/Library/Preferences/AppCode*"))))

            dots.extend(
                map(lambda dst: Dotfile(src="RubyMine", dst=dst),
                    glob.glob(os.path.expanduser("~/Library/Preferences/RubyMine*"))))

        return dots

    def templates(self):
        return [
            Template(src="shrc", dst="~/.shrc"),

            Template(src="bashrc", dst="~/.bashrc"),
            Template(src="bash_profile", dst="~/.bash_profile"),

            Template(src="zshrc", dst="~/.zshrc"),
            Template(src="zshprofile", dst="~/.zshprofile"),
        ]


class Install(DotfileAction):
    def run(self):
        for dot in self.dotfiles():
            if dot.src.startswith('/'):
                self.__run(dot)
            else:
                self.__run(dot, sysname=xos.sysname())
                self.__run(dot, sysname="default")

            if dot.install:
                dot.install()

        for template in self.templates():
            self.__enable(template)

        return

    def __run(self, dotfile, sysname="default"):
        if not self.__istarget(dotfile):
            if self.logger:
                self.logger.info("File is not target: %s" % os.path.relpath(dotfile.src, os.getcwd()))
            return

        if dotfile.src.startswith('/'):
            src = dotfile.src 
        else:
            src = os.path.abspath(os.path.join(sysname, dotfile.src))

        if dotfile.dst.startswith('/'):
            dst = dotfile.dst 
        else:
            dst = os.path.expanduser(dotfile.dst)

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
                new_dst = os.path.join(dotfile.dst, rel_dst)
                new_dot = Dotfile(src=new_src, dst=new_dst)
                self.__run(new_dot, sysname=sysname)

        return True

    def __enable(self, template):

        #
        # source
        #
        src_path = os.path.join(TEMPLATE_DIR, template.src)

        if not os.path.exists(src_path):
            return

        src_str = ""
        with open(src_path, "r") as src_file:
            src_str = src_file.read().strip()

        #
        # destination
        #
        dst_path = os.path.expanduser(template.dst)

        # new file
        if not os.path.exists(dst_path):
            with open(dst_path, "w") as dst_file:
                if self.logger:
                    self.logger.execute("Enable %s" % xos.xpath.reduceuser(src_path))
                if not self.noop:
                    dst_file.write(src_str + "\n")
            return

        dst_str = ""
        with open(dst_path, "r") as dst_file:
            dst_str = dst_file.read()

        # skip: already enabled
        if src_str in dst_str:
            if self.logger:
                self.logger.info("Already enabled: %s" % xos.xpath.reduceuser(dst_path))
            return

        # enable
        if self.logger:
            self.logger.execute("Enable %s" % xos.xpath.reduceuser(src_path))

        if not self.noop:
            with open(dst_path, "w") as dst_file:
                dst_file.write(dst_str + src_str + "\n")

        return

    def __istarget(self, dotfile):
        patterns = [
            '\.swp$'
        ]

        for pattern in patterns:
            if re.search(pattern, dotfile.src):
                return False

        return True


class Uninstall(DotfileAction):
    def run(self):
        for dot in self.dotfiles():
            self.__run(dot, sysname=xos.sysname())
            self.__run(dot, sysname="default")

            if dot.uninstall:
                dot.uninstall()

        for template in self.templates():
            self.__disable(template)

        return

    def __run(self, dotfile, sysname="default"):
        if not self.__istarget(dotfile):
            if self.logger:
                self.logger.info("File is not target: %s" % os.path.relpath(dotfile.src, os.getcwd()))
            return

        src = os.path.abspath(os.path.join(sysname, dotfile.src))
        dst = os.path.expanduser(dotfile.dst)

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
                new_dst = os.path.join(dotfile.dst, rel_dst)
                new_dot = Dotfile(src=new_src, dst=new_dst)
                self.__run(new_dot, sysname=sysname)

        return True

    def __disable(self, template):

        #
        # source
        #
        src_path = os.path.join(TEMPLATE_DIR, template.src)

        if not os.path.exists(src_path):
            return

        src_str = ""
        with open(src_path, "r") as src_file:
            src_str = src_file.read().strip()

        #
        # destination
        #
        dst_path = os.path.expanduser(template.dst)

        # not found
        if not os.path.exists(dst_path):
            self.logger.info("File NOT FOUND: %s" % xos.xpath.reduceuser(dst_path))
            return

        dst_str = ""
        with open(dst_path, "r") as dst_file:
            dst_str = dst_file.read()

        # skip: already disabled
        if not src_str in dst_str:
            if self.logger:
                self.logger.info("Already disabled: %s" % xos.xpath.reduceuser(dst_path))
            return

        # disable
        if self.logger:
            self.logger.execute("Disable %s" % xos.xpath.reduceuser(src_path))

        if not self.noop:
            with open(dst_path, "w") as dst_file:
                dst_file.write(dst_str.replace(src_str, ""))

        return

    def __istarget(self, dotfile):
        patterns = [
            '\.swp$'
        ]

        for pattern in patterns:
            if re.search(pattern, dotfile.src):
                return False

        return True

class Status(DotfileAction):
    def run(self):
        dotfiles = sorted(self.dotfiles(), key=lambda x: x.dst)

        for dot in dotfiles:

            target = os.path.expanduser(dot.dst)

            if not os.path.exists(target):
                continue

            if xos.isdarwin():
                self.shell.execute("ls -lFG %s" % target)
            else:
                self.shell.execute("ls -lFo %s" % target)

        return True


class Dotfile:
    def __init__(self, src, dst, install=None, uninstall=None):
        self.src = src
        self.dst = dst
        self.install = install
        self.uninstall = uninstall
        return


class Template:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst
