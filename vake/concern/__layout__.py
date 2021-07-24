# 1st
import os
import re

from dataclasses import dataclass
from typing import List

# 2nd
from .. import filetree
from .. import kernel
from . import __base__

STATIC_DIR = "./static"
SNIPPET_DIR = "./snippet"


@dataclass
class Recipe:
    src: str
    dst: str
    activate: __base__.Action = None
    deactivate: __base__.Action = None


class LayoutAction(__base__.Action):
    def dotfiles(self) -> List[Recipe]:
        dots = []

        # shared
        dots.extend([
            # sh
            Recipe(
                src="sh.d",
                dst="~/.sh.d"
            ),

            # bash
            Recipe(
                src="bash.d",
                dst="~/.bash.d"
            ),
            Recipe(
                src="bash_completion.d",
                dst="~/.bash_completion.d"
            ),

            # zsh
            Recipe(
                src="zsh.d",
                dst="~/.zsh.d"
            ),
            Recipe(
                src="zsh-completions",
                dst="~/.zsh-completions"
            ),
            Recipe(
                src="/usr/local/library/Contributions/brew_zsh_completion.zsh",
                dst="~/.zsh-completions/_brew"
            ),

            # git
            Recipe(
                src="gitconfig",
                dst="~/.gitconfig"
            ),
            Recipe(
                src="tigrc",
                dst="~/.tigrc"
            ),

            # vim
            Recipe(
                src="vimrc",
                dst="~/.vimrc"
            ),
            Recipe(
                src="vim",
                dst="~/.vim",
                activate=VimActivateAction(noop=self.noop, logger=self.logger),
                deactivate=None
            ),

            # ext
            Recipe(
                src="asdfrc",
                dst="~/.asdfrc"
            ),
            Recipe(
                src="tmux.conf",
                dst="~/.tmux.conf"
            ),

            # gradle
            Recipe(
                src="gradle",
                dst="~/.gradle"
            ),
        ])

        # linux
        if kernel.islinux():
            dots.extend([])

        # darwin
        if kernel.isdarwin():
            dots.extend([
                Recipe(src="Xcode", dst=dst) for dst in
                filetree.pilot(
                    "~/Library/Developer/Xcode").expanduser().glob()
            ])
            dots.extend([
                Recipe(src="IntelliJIdea", dst=dst) for dst in
                filetree.pilot(
                    "~/Library/Preferences/IntelliJIdea*").expanduser().glob()
            ])
            dots.extend([
                Recipe(src="IntelliJIdea", dst=dst) for dst in
                filetree.pilot(
                    "~/Library/ApplicationSupport/JetBrains/IntelliJIdea*").expanduser().glob()
            ])
            dots.extend([
                Recipe(src="AndroidStudio", dst=dst) for dst in
                filetree.pilot(
                    "~/Library/Preferences/AndroidStudio*").expanduser().glob()
            ])
            dots.extend([
                Recipe(src="AndroidStudio", dst=dst) for dst in
                filetree.pilot(
                    "~/Library/ApplicationSupport/Google/AndroidStudio*").expanduser().glob()
            ])
            dots.extend([
                Recipe(src="AppCode", dst=dst) for dst in
                filetree.pilot(
                    "~/Library/Preferences/AppCode*").expanduser().glob()
            ])
            dots.extend([
                Recipe(src="AppCode", dst=dst) for dst in
                filetree.pilot(
                    "~/Library/ApplicationSupport/JetBrains/AppCode*").expanduser().glob()
            ])
            dots.extend([
                Recipe(src="RubyMine", dst=dst) for dst in
                filetree.pilot(
                    "~/Library/Preferences/RubyMine*").expanduser().glob()
            ])
            dots.extend([
                Recipe(src="RubyMine", dst=dst) for dst in
                filetree.pilot(
                    "~/Library/ApplicationSupport/JetBrains/RubyMine*").expanduser().glob()
            ])
            dots.extend([
                Recipe(src="GoLand", dst=dst) for dst in
                filetree.pilot(
                    "~/Library/Preferences/GoLand*").expanduser().glob()
            ])
            dots.extend([
                Recipe(src="GoLand", dst=dst) for dst in
                filetree.pilot(
                    "~/Library/ApplicationSupport/JetBrains/GoLand*").expanduser().glob()
            ])
            dots.extend([
                Recipe(src="CLion", dst=dst) for dst in
                filetree.pilot(
                    "~/Library/Preferences/CLion*").expanduser().glob()
            ])
            dots.extend([
                Recipe(src="CLion", dst=dst) for dst in
                filetree.pilot(
                    "~/Library/ApplicationSupport/JetBrains/CLion*").expanduser().glob()
            ])
            dots.extend([
                Recipe(src="Rider", dst=dst) for dst in
                filetree.pilot(
                    "~/Library/Preferences/Rider*").expanduser().glob()
            ])
            dots.extend([
                Recipe(src="Rider", dst=dst) for dst in
                filetree.pilot(
                    "~/Library/ApplicationSupport/JetBrains/Rider*").expanduser().glob()
            ])

        return dots

    def snippets(self) -> List[Recipe]:
        return [
            # sh
            Recipe(
                src="shrc",
                dst="~/.shrc"
            ),

            # bash
            Recipe(
                src="bashrc",
                dst="~/.bashrc"
            ),
            Recipe(
                src="bash_profile",
                dst="~/.bash_profile"
            ),

            # zsh
            Recipe(
                src="zshrc",
                dst="~/.zshrc"
            ),
            Recipe(
                src="zshprofile",
                dst="~/.zshprofile"
            ),
        ]

    def binfiles(self) -> List[Recipe]:
        return [
            Recipe(
                src="bin",
                dst="~/.bin"
            )
        ]


class InstallAction(LayoutAction):
    def run(self):
        for dot in self.dotfiles():
            if dot.src.startswith('/'):
                self.__run(dot)
            else:
                self.__run(dot, sysname=kernel.sysname())
                self.__run(dot, sysname="default")

            if dot.activate:
                dot.activate.run()

        for snippet in self.snippets():
            self.__enable(snippet)

        for bin in self.binfiles():
            self.__run(bin, sysname=kernel.sysname())
            self.__run(bin, sysname="default")

        return

    def __run(self, recipe, sysname="default"):
        if not self.__istarget(recipe):
            if self.logger:
                relpath = filetree.pilot(recipe.src)\
                    .prepend(sysname)\
                    .prepend(STATIC_DIR)\
                    .relpath(os.getcwd())
                self.logger.info("File is not target: %s" % relpath)
            return

        if recipe.src.startswith('/'):
            src = filetree.pilot(recipe.src)
        else:
            src = filetree.pilot(recipe.src)\
                .prepend(sysname)\
                .prepend(STATIC_DIR).abspath()

        if recipe.dst.startswith('/'):
            dst = filetree.pilot(recipe.dst)
        else:
            dst = filetree.pilot(recipe.dst).expanduser()

        #
        # guard
        #

        # src not found
        if not src.exists():
            return False

        # dst link already exists
        if dst.islink():
            if self.logger:
                self.logger.info(
                    "Symlink already exists: %s" % dst.reduceuser()
                )
            return False

        #
        # file
        #
        if src.isfile():
            # another file already exists
            if dst.isfile():
                if self.logger:
                    self.logger.info(
                        "File already exists: %s" % dst.reduceuser()
                    )
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
                new_dst = filetree.pilot(recipe.dst)\
                    .append(new_src.relpath(src))
                new_recipe = Recipe(
                    src=new_src.pathname(),
                    dst=new_dst.pathname()
                )
                self.__run(new_recipe, sysname=sysname)

        return True

    def __enable(self, snippet):

        #
        # source
        #
        src = filetree.pilot(snippet.src).prepend(SNIPPET_DIR)

        if not src.exists():
            return

        src_str = src.read().strip()

        #
        # destination
        #
        dst = filetree.pilot(snippet.dst).expanduser()

        # new file
        if not dst.exists():
            if self.logger:
                self.logger.execute("Enable snippet %s" % src.reduceuser())

            if not self.noop:
                dst.write(src_str + "\n")

            return

        dst_str = dst.read()

        # skip: already enabled
        if src_str in dst_str:
            if self.logger:
                self.logger.info(
                    "Snippet already enabled: %s" % dst.reduceuser()
                )
            return

        # enable
        if self.logger:
            self.logger.execute("Enable %s" % src.reduceuser())

        if not self.noop:
            dst.write(dst_str + src_str + "\n")

        return

    def __istarget(self, dotfile):
        blacklist = [r'\.swp$', r'\.bak$', r'\.DS_Store$']

        for pattern in blacklist:
            if re.search(pattern, dotfile.src):
                return False

        return True


class UninstallAction(LayoutAction):
    def run(self):
        for dot in self.dotfiles():
            self.__run(dot, sysname=kernel.sysname())
            self.__run(dot, sysname="default")

            if dot.deactivate:
                dot.deactivate.run()

        for snippet in self.snippets():
            self.__disable(snippet)

        for bin in self.binfiles():
            self.__run(bin, sysname=kernel.sysname())
            self.__run(bin, sysname="default")

        return

    def __run(self, recipe, sysname="default"):
        if not self.__istarget(recipe):
            if self.logger:
                relpath = filetree.pilot(recipe.src)\
                    .prepend(sysname)\
                    .prepend(STATIC_DIR)\
                    .relpath(os.getcwd())
                self.logger.info("File is not target: %s" % relpath)
            return

        if recipe.src.startswith('/'):
            src = filetree.pilot(recipe.src)
        else:
            src = filetree.pilot(recipe.src)\
                .prepend(sysname)\
                .prepend(STATIC_DIR).abspath()

        if recipe.dst.startswith('/'):
            dst = filetree.pilot(recipe.dst)
        else:
            dst = filetree.pilot(recipe.dst).expanduser()


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
                new_dst = filetree.pilot(recipe.dst)\
                    .append(new_src.relpath(src))
                new_recipe = Recipe(
                    src=new_src.pathname(),
                    dst=new_dst.pathname()
                )
                self.__run(new_recipe, sysname=sysname)

        return True

    def __disable(self, snippet):

        #
        # source
        #
        src = filetree.pilot(snippet.src).prepend(SNIPPET_DIR)

        if not src.exists():
            return

        src_str = src.read().strip()

        #
        # destination
        #
        dst = filetree.pilot(snippet.dst).expanduser()

        # not found
        if not dst.exists():
            self.logger.info("File NOT FOUND: %s" % dst.reduceuser())
            return

        dst_str = dst.read()

        # skip: already disabled
        if not src_str in dst_str:
            if self.logger:
                self.logger.info(
                    "Snippet already disabled: %s" % dst.reduceuser()
                )
            return

        # disable
        if self.logger:
            self.logger.execute("Disable snippet %s" % src.reduceuser())

        if not self.noop:
            dst.write(dst_str.replace(src_str, ""))

        return

    def __istarget(self, dotfile):
        blacklist = [r'\.swp$', r'\.DS_Store$']

        for pattern in blacklist:
            if re.search(pattern, dotfile.src):
                return False

        return True


class StatusAction(LayoutAction):
    def run(self):
        dotfiles = sorted(self.dotfiles(), key=lambda x: x.dst)

        for dot in dotfiles:
            target = filetree.pilot(dot.dst).expanduser()

            if not target.exists():
                continue

            if kernel.isdarwin():
                self.shell.execute("ls -lFG %s" % target)
            else:
                self.shell.execute("ls -lFo %s" % target)

        return True


class VimActivateAction(__base__.Action):

    def run(self):
        dst = filetree.pilot("~/.vim/autoload/plug.vim").expanduser()

        if dst.isfile():
            self.logger.info(
                "Vim-Plug is already downloaded: %s" % dst.reduceuser()
            )
            return None

        self.shell.execute([
            "curl",
            "--fail",
            "--location",
            "--create-dirs",
            "--output", str(dst),
            "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim"
        ])
        return None
