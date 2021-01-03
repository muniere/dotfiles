# 1st
import sys
import argparse
import logging

# 2nd
from .. import concern
from .. import winston


def cli():
    return CLI()


class Action:
    INSTALL = "install"
    UNINSTALL = "uninstall"
    STATUS = "status"
    COMPLETION = "completion"

    @classmethod
    def values(cls):
        return [
            cls.INSTALL,
            cls.UNINSTALL,
            cls.STATUS,
            cls.COMPLETION,
        ]


class Target:
    DOTFILE = "dotfile"
    BINFILE = "binfile"
    BREW = "brew"
    CASK = "cask"

    @classmethod
    def values(cls):
        return [
            cls.DOTFILE,
            cls.BINFILE,
            cls.BREW,
            cls.CASK,
        ]


class Concern:

    @classmethod
    def hunt(cls, target):
        if target == Target.DOTFILE:
            return concern.dotfile

        if target == Target.BREW:
            return concern.brew

        if target == Target.CASK:
            return concern.cask

        if target == Target.BINFILE:
            return concern.binfile

        return None

    @classmethod
    def installable(cls, x):
        return x is not None and x.Install is not None

    @classmethod
    def uninstallable(cls, x):
        return x is not None and x.Uninstall is not None

    @classmethod
    def statusable(cls, x):
        return x is not None and x.Status is not None


class Completion:
    SOURCE = "vake/template/_xake"
    DESTINATION = "default/zsh-completions/_xake"


class Context:
    """
    Attributes store for application
    """

    @classmethod
    def parse(cls, args: list[str]) -> 'Context':
        """
        Compose context for arguments

        :param args: Arguments
        :return: Context
        """
        parser = cls.__make_argparser()
        namespace = parser.parse_args(args)

        context = Context()
        context.action = namespace.action
        context.targets = namespace.target or ["dotfile", "binfile"]
        context.dry_run = namespace.dry_run
        context.verbose = namespace.verbose

        return context

    @classmethod
    def options(cls):
        """
        Returns all available options

        :return: List of available options
        """
        parser = cls.__make_argparser()
        return parser._optionals._group_actions

    @classmethod
    def __make_argparser(cls) -> argparse.ArgumentParser:
        """
        Create a new ArgumentParser.

        :return: New argument parser
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("-n", "--dry-run",
                            dest="dry_run",
                            action="store_true",
                            help="Do not execute commands actually")
        parser.add_argument("-v", "--verbose",
                            dest="verbose",
                            action="store_true",
                            help="Show verbose messages")
        parser.add_argument("action",
                            type=str,
                            help="Action to perform: (%s)" % "|".join(Action.values()))
        parser.add_argument("target",
                            type=str,
                            nargs="*",
                            help="Target for action: (%s)" % "|".join(Target.values()))
        return parser

    def __init__(self):
        """
        Initialize context
        """
        self.action = None
        self.targets = []
        self.dry_run = False
        self.verbose = False
        return

    def logger(self) -> logging.Logger:
        """
        Create a new logger.

        :return: New logger instance
        """
        if self.verbose:
            level = winston.DEBUG
        else:
            level = winston.EXEC

        formatter = winston.LabelFormatter()

        handler = winston.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(formatter)

        logger = winston.getLogger(__name__)
        logger.setLevel(level)
        logger.addHandler(handler)

        return logger


class CLI:
    """
    CLI launcher
    """

    def __init__(self):
        """
        Initialize application
        """
        pass

    def run(self, args: list[str]) -> None:
        """
        Run application with given arguments.

        :param args: CLI arguments
        """

        # logging
        winston.bootstrap()

        # context
        context = Context.parse(args)

        # actions
        if context.action == Action.INSTALL:
            self.__install(context)
            sys.exit(0)

        if context.action == Action.UNINSTALL:
            self.__uninstall(context)
            sys.exit(0)

        if context.action == Action.STATUS:
            self.__status(context)
            sys.exit(0)

        if context.action == Action.COMPLETION:
            self.__completion(context)
            sys.exit(0)

        sys.exit(1)

    @staticmethod
    def __install(context: Context) -> None:
        """
        Perform install action.

        :param context: Context
        """

        noop = context.dry_run
        logger = context.logger()

        concerns = [Concern.hunt(t) for t in context.targets]
        concerns = [x for x in concerns if Concern.installable(x)]
        commands = [x.Install(noop=noop, logger=logger) for x in concerns]

        for command in commands:
            command.run()

        return

    @staticmethod
    def __uninstall(context: Context) -> None:
        """
        Perform uninstall action.

        :param context: Context
        """
        noop = context.dry_run
        logger = context.logger()

        concerns = [Concern.hunt(t) for t in context.targets]
        concerns = [x for x in concerns if Concern.uninstallable(x)]
        commands = [x.Uninstall(noop=noop, logger=logger) for x in concerns]

        for command in commands:
            command.run()

        return

    @staticmethod
    def __status(context: Context) -> None:
        """
        Perform status action.

        :param context: Context
        """
        noop = context.dry_run
        logger = context.logger()

        concerns = [Concern.hunt(t) for t in context.targets]
        concerns = [x for x in concerns if Concern.statusable(x)]
        commands = [x.Status(noop=noop, logger=logger) for x in concerns]

        for command in commands:
            command.run()

        return

    @staticmethod
    def __completion(context: Context) -> None:
        """
        Perform completion action.

        :param context: Context
        """

        from mako.template import Template

        template = Template(
            filename=Completion.SOURCE,
            input_encoding="utf-8",
            output_encoding="utf-8",
            bytestring_passthrough=True,
        )

        rendered = template.render(
            options=Context.options(),
            actions=Action.values(),
            targets=Target.values(),
        )

        with open(Completion.DESTINATION, 'w') as dst:
            dst.write(rendered)

        sys.stdout.write(rendered)
        return
