# 1st
import os
import glob
import re

# 2nd
from .. import fs
from .. import osx
from . import base

TEMPLATE_DIR = "./vake/template"


class DotfileAction(base.Action):
    def __vim_install(self):
        self.shell.git_clone(
            src="https://github.com/Shougo/neobundle.vim",
            dst=fs.pilot("~/.vim/bundle/neobundle.vim").expanduser().pathname()
        )
        return None

    def __vim_uninstall(self):
        return None

    def dotfiles(self):
        dots = []

        # shared
        dots.extend([
            # sh
            Dotfile(
                src="sh.d",
                dst="~/.sh.d"
            ),

            # bash
            Dotfile(
                src="bash.d",
                dst="~/.bash.d"
            ),
            Dotfile(
                src="bash_completion.d",
                dst="~/.bash_completion.d"
            ),

            # zsh
            Dotfile(
                src="zsh.d",
                dst="~/.zsh.d"
            ),
            Dotfile(
                src="zsh-completions",
                dst="~/.zsh-completions"
            ),
            Dotfile(
                src="/usr/local/library/Contributions/brew_zsh_completion.zsh",
                dst="~/.zsh-completions/_brew"
            ),

            # git
            Dotfile(
                src="gitconfig",
                dst="~/.gitconfig"
            ),
            Dotfile(
                src="tigrc",
                dst="~/.tigrc"
            ),

            # vim
            Dotfile(
                src="vimrc",
                dst="~/.vimrc"
            ),
            Dotfile(
                src="vim",
                dst="~/.vim",
                install=self.__vim_install,
                uninstall=self.__vim_uninstall
            ),

            # ext
            Dotfile(
                src="tmux.conf",
                dst="~/.tmux.conf"
            ),
            Dotfile(
                src="peco",
                dst="~/.peco"
            ),

            # gradle
            Dotfile(
                src="gradle",
                dst="~/.gradle"
            ),
        ])

        # linux
        if osx.islinux():
            dots.extend([])

        # darwin
        if osx.isdarwin():
            dots.extend([
                Dotfile(src="Xcode", dst=dst) for dst in
                fs.pilot("~/Library/Developer/Xcode").expanduser().glob()
            ])
            dots.extend([
                Dotfile(src="IntelliJIdea", dst=dst) for dst in
                fs.pilot("~/Library/Preferences/IntelliJIdea*").expanduser().glob()
            ])
            dots.extend([
                Dotfile(src="AndroidStudio", dst=dst) for dst in
                fs.pilot("~/Library/Preferences/AndroidStudio*").expanduser().glob()
            ])
            dots.extend([
                Dotfile(src="AppCode", dst=dst) for dst in
                fs.pilot("~/Library/Preferences/AppCode*").expanduser().glob()
            ])
            dots.extend([
                Dotfile(src="RubyMine", dst=dst) for dst in
                fs.pilot("~/Library/Preferences/RubyMine*").expanduser().glob()
            ])

        return dots

    def templates(self):
        return [
            # sh
            Template(
                src="shrc",
                dst="~/.shrc"
            ),

            # bash
            Template(
                src="bashrc",
                dst="~/.bashrc"
            ),
            Template(
                src="bash_profile",
                dst="~/.bash_profile"
            ),

            # zsh
            Template(
                src="zshrc",
                dst="~/.zshrc"
            ),
            Template(
                src="zshprofile",
                dst="~/.zshprofile"
            ),
        ]


class Install(DotfileAction):
    def run(self):
        for dot in self.dotfiles():
            if dot.src.startswith('/'):
                self.__run(dot)
            else:
                self.__run(dot, sysname=osx.sysname())
                self.__run(dot, sysname="default")

            if dot.install:
                dot.install()

        for template in self.templates():
            self.__enable(template)

        return

    def __run(self, dotfile, sysname="default"):
        if not self.__istarget(dotfile):
            if self.logger:
                relpath = fs.pilot(dotfile.src).relpath(os.getcwd())
                self.logger.info("File is not target: %s" % relpath)
            return

        if dotfile.src.startswith('/'):
            src = fs.pilot(dotfile.src)
        else:
            src = fs.pilot(dotfile.src).prepend(sysname).abspath()

        if dotfile.dst.startswith('/'):
            dst = fs.pilot(dotfile.dst)
        else:
            dst = fs.pilot(dotfile.dst).expanduser()

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
                new_dst = fs.pilot(dotfile.dst).append(new_src.relpath(src))
                new_dot = Dotfile(src=new_src.pathname(), dst=new_dst.pathname())
                self.__run(new_dot, sysname=sysname)

        return True

    def __enable(self, template):

        #
        # source
        #
        src = fs.pilot(template.src).prepend(TEMPLATE_DIR)

        if not src.exists():
            return

        src_str = src.read().strip()

        #
        # destination
        #
        dst = fs.pilot(template.dst).expanduser()

        # new file
        if not dst.exists():
            if self.logger:
                self.logger.execute("Enable %s" % src.reduceuser())

            if not self.noop:
                dst.write(src_str + "\n")

            return

        dst_str = dst.read()

        # skip: already enabled
        if src_str in dst_str:
            if self.logger:
                self.logger.info("Already enabled: %s" % dst.reduceuser())
            return

        # enable
        if self.logger:
            self.logger.execute("Enable %s" % src.reduceuser())

        if not self.noop:
            dst.write(dst_str + src_str + "\n")

        return

    def __istarget(self, dotfile):
        blacklist = [r'\.swp$']

        for pattern in blacklist:
            if re.search(pattern, dotfile.src):
                return False

        return True


class Uninstall(DotfileAction):
    def run(self):
        for dot in self.dotfiles():
            self.__run(dot, sysname=osx.sysname())
            self.__run(dot, sysname="default")

            if dot.uninstall:
                dot.uninstall()

        for template in self.templates():
            self.__disable(template)

        return

    def __run(self, dotfile, sysname="default"):
        if not self.__istarget(dotfile):
            if self.logger:
                relpath = fs.pilot(dotfile.src).relpath(os.getcwd())
                self.logger.info("File is not target: %s" % relpath)
            return

        src = fs.pilot(dotfile.src).prepend(sysname).abspath()
        dst = fs.pilot(dotfile.dst).expanduser()

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
                new_dst = fs.pilot(dotfile.dst).append(new_src.relpath(src))
                new_dot = Dotfile(src=new_src.pathname(), dst=new_dst.pathname())
                self.__run(new_dot, sysname=sysname)

        return True

    def __disable(self, template):

        #
        # source
        #
        src = fs.pilot(template.src).prepend(TEMPLATE_DIR)

        if not src.exists():
            return

        src_str = src.read().strip()

        #
        # destination
        #
        dst = fs.pilot(template.dst).expanduser()

        # not found
        if not dst.exists():
            self.logger.info("File NOT FOUND: %s" % dst.reduceuser())
            return

        dst_str = dst.read()

        # skip: already disabled
        if not src_str in dst_str:
            if self.logger:
                self.logger.info("Already disabled: %s" % dst.reduceuser())
            return

        # disable
        if self.logger:
            self.logger.execute("Disable %s" % src.reduceuser())

        if not self.noop:
            dst.write(dst_str.replace(src_str, ""))

        return

    def __istarget(self, dotfile):
        blacklist = [r'\.swp$']

        for pattern in blacklist:
            if re.search(pattern, dotfile.src):
                return False

        return True


class Status(DotfileAction):
    def run(self):
        dotfiles = sorted(self.dotfiles(), key=lambda x: x.dst)

        for dot in dotfiles:
            target = fs.pilot(dot.dst).expanduser()

            if not target.exists():
                continue

            if osx.isdarwin():
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
