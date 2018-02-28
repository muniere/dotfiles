# 1st
import glob
import re

# 2nd
from .. import xos
from ..xos import xpath

# 3rd
import base

TEMPLATE_DIR = "./vake/template"


class DotfileAction(base.Action):
    def __vim_install(self):
        self.shell.git_clone(
            src="https://github.com/Shougo/neobundle.vim",
            dst=xpath.expanduser("~/.vim/bundle/neobundle.vim")
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
                map(lambda dst: Dotfile(src="IntelliJIdea", dst=dst),
                    glob.glob(xpath.expanduser("~/Library/Preferences/IntelliJIdea*"))))

            dots.extend(
                map(lambda dst: Dotfile(src="AndroidStudio", dst=dst),
                    glob.glob(xpath.expanduser("~/Library/Preferences/AndroidStudio*"))))

            dots.extend(
                map(lambda dst: Dotfile(src="AppCode", dst=dst),
                    glob.glob(xpath.expanduser("~/Library/Preferences/AppCode*"))))

            dots.extend(
                map(lambda dst: Dotfile(src="RubyMine", dst=dst),
                    glob.glob(xpath.expanduser("~/Library/Preferences/RubyMine*"))))

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
                self.logger.info("File is not target: %s" % xpath.relpath(dotfile.src, xos.getcwd()))
            return

        if dotfile.src.startswith('/'):
            src = dotfile.src 
        else:
            src = xpath.abspath(xpath.join(sysname, dotfile.src))

        if dotfile.dst.startswith('/'):
            dst = dotfile.dst 
        else:
            dst = xpath.expanduser(dotfile.dst)

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
                new_dst = xpath.join(dotfile.dst, rel_dst)
                new_dot = Dotfile(src=new_src, dst=new_dst)
                self.__run(new_dot, sysname=sysname)

        return True

    def __enable(self, template):

        #
        # source
        #
        src_path = xpath.join(TEMPLATE_DIR, template.src)

        if not xpath.exists(src_path):
            return

        src_str = ""
        with open(src_path, "r") as src_file:
            src_str = src_file.read().strip()

        #
        # destination
        #
        dst_path = xpath.expanduser(template.dst)

        # new file
        if not xpath.exists(dst_path):
            with open(dst_path, "w") as dst_file:
                if self.logger:
                    self.logger.execute("Enable %s" % xpath.reduceuser(src_path))
                if not self.noop:
                    dst_file.write(src_str + "\n")
            return

        dst_str = ""
        with open(dst_path, "r") as dst_file:
            dst_str = dst_file.read()

        # skip: already enabled
        if src_str in dst_str:
            if self.logger:
                self.logger.info("Already enabled: %s" % xpath.reduceuser(dst_path))
            return

        # enable
        if self.logger:
            self.logger.execute("Enable %s" % xpath.reduceuser(src_path))

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
                self.logger.info("File is not target: %s" % xpath.relpath(dotfile.src, xos.getcwd()))
            return

        src = xpath.abspath(xpath.join(sysname, dotfile.src))
        dst = xpath.expanduser(dotfile.dst)

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
                new_dst = xpath.join(dotfile.dst, rel_dst)
                new_dot = Dotfile(src=new_src, dst=new_dst)
                self.__run(new_dot, sysname=sysname)

        return True

    def __disable(self, template):

        #
        # source
        #
        src_path = xpath.join(TEMPLATE_DIR, template.src)

        if not xpath.exists(src_path):
            return

        src_str = ""
        with open(src_path, "r") as src_file:
            src_str = src_file.read().strip()

        #
        # destination
        #
        dst_path = xpath.expanduser(template.dst)

        # not found
        if not xpath.exists(dst_path):
            self.logger.info("File NOT FOUND: %s" % xpath.reduceuser(dst_path))
            return

        dst_str = ""
        with open(dst_path, "r") as dst_file:
            dst_str = dst_file.read()

        # skip: already disabled
        if not src_str in dst_str:
            if self.logger:
                self.logger.info("Already disabled: %s" % xpath.reduceuser(dst_path))
            return

        # disable
        if self.logger:
            self.logger.execute("Disable %s" % xpath.reduceuser(src_path))

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

            target = xpath.expanduser(dot.dst)

            if not xpath.exists(target):
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
