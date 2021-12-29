import argparse
import sys
from enum import Enum
from typing import List

from . import intent
from . import kernel
from . import winston

__all__ = [
    'cli'
]


def cli():
    return CLI()


class Action(Enum):
    DEPLOY = "deploy"
    UNDEPLOY = "undeploy"
    INSTALL = "install"
    UNINSTALL = "uninstall"
    STATUS = "status"
    COMPLETION = "completion"


class Completion:
    SOURCE = "template/_xake"
    DESTINATION = "static/default/zsh-completions/_xake"


class Context:
    """
    Attributes store for application
    """

    @classmethod
    def parse(cls, args: List[str]) -> 'Context':
        """
        Compose context for arguments

        :param args: Arguments
        :return: Context
        """
        parser = Context.__make_argparser()
        namespace = parser.parse_args(args)

        context = Context()
        context.action = Action(namespace.action)
        context.dry_run = namespace.dry_run
        context.verbose = namespace.verbose

        return context

    @classmethod
    def options(cls):
        """
        Returns all available options

        :return: List of available options
        """
        parser = Context.__make_argparser()

        # pylint: disable=protected-access
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
                            help="Action to perform: (%s)" % "|".join([x.value for x in Action]))
        return parser

    def __init__(self):
        """
        Initialize context
        """
        self.action = None
        self.dry_run = False
        self.verbose = False
        return

    def logger(self) -> winston.LoggerWrapper:
        """
        Create a new logger.

        :return: New logger instance
        """
        if self.verbose:
            level = winston.DEBUG
        else:
            level = winston.EXEC

        formatter = winston.ColoredFormatter()

        handler = winston.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(formatter)

        logger = winston.get_logger(__name__)
        logger.set_level(level)
        logger.add_handler(handler)

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

    def run(self, args: List[str]) -> None:
        """
        Run application with given arguments.

        :param args: CLI arguments
        """

        # logging
        winston.bootstrap()

        # context
        context = Context.parse(args)

        # actions
        if context.action == Action.DEPLOY:
            self.__deploy(context)
            sys.exit(0)

        if context.action == Action.UNDEPLOY:
            self.__undeploy(context)
            sys.exit(0)

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
            self.__completion()
            sys.exit(0)

        sys.exit(1)

    @staticmethod
    def __deploy(context: Context) -> None:
        """
        Perform tune action.

        :param context: Context
        """

        noop = context.dry_run
        logger = context.logger()

        commands = [
            intent.PrefInstallAction(noop=noop, logger=logger),
        ]

        for command in commands:
            command.run()

        return

    @staticmethod
    def __undeploy(context: Context) -> None:
        """
        Perform untine action.

        :param context: Context
        """
        noop = context.dry_run
        logger = context.logger()

        commands = [
            intent.PrefUninstallAction(noop=noop, logger=logger),
        ]

        for command in commands:
            command.run()

        return

    @staticmethod
    def __install(context: Context) -> None:
        """
        Perform install action.

        :param context: Context
        """

        noop = context.dry_run
        logger = context.logger()

        commands = []

        if kernel.islinux():
            commands.extend([])

        if kernel.isdarwin():
            commands.extend([
                intent.BrewInstallAction(noop=noop, logger=logger),
            ])

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

        commands = [
            intent.BrewUninstallAction(noop=noop, logger=logger),
        ]

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

        commands = [
            intent.PrefStatusAction(noop=noop, logger=logger),
            intent.BrewStatusAction(noop=noop, logger=logger),
        ]

        for command in commands:
            command.run()

        return

    @staticmethod
    def __completion() -> None:
        """
        Perform completion action.
        """

        # pylint: disable=import-outside-toplevel
        from mako.template import Template

        template = Template(
            filename=Completion.SOURCE,
            input_encoding="utf-8",
            output_encoding="utf-8",
            bytestring_passthrough=True,
        )

        rendered = template.render(
            options=Context.options(),
            actions=[x.value for x in Action],
        )

        with open(Completion.DESTINATION, 'w') as dst:
            dst.write(rendered)

        sys.stdout.write(rendered)
        return
