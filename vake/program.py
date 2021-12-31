import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum
from typing import List

from . import timber
from .intent import BrewInstallAction, BrewUninstallAction, BrewStatusAction
from .intent import PrefInstallAction, PrefUninstallAction, PrefStatusAction
from .kernel import Identity
from .timber import Level, ColoredFormatter, StreamHandler, Lumber

__all__ = [
    'CLI'
]


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


@dataclass(frozen=True)
class Context:
    action: Action
    dry_run: bool
    verbose: bool

    def logger(self) -> Lumber:
        """
        Create a new logger.

        :return: New logger instance
        """
        if self.verbose:
            level = Level.DEBUG
        else:
            level = Level.EXEC

        formatter = ColoredFormatter()

        handler = StreamHandler()
        handler.set_level(level)
        handler.set_formatter(formatter)

        logger = timber.get_logger(__name__)
        logger.set_level(level)
        logger.add_handler(handler)

        return logger


class ContextParser:
    delegate: ArgumentParser

    def __init__(self):
        self.delegate = ArgumentParser()
        self.delegate.add_argument("-n", "--dry-run",
                                   dest="dry_run",
                                   action="store_true",
                                   help="Do not execute commands actually")
        self.delegate.add_argument("-v", "--verbose",
                                   dest="verbose",
                                   action="store_true",
                                   help="Show verbose messages")
        self.delegate.add_argument("action",
                                   type=str,
                                   help="Action to perform: (%s)" % "|".join([x.value for x in Action]))

    def parse(self, args: List[str]) -> 'Context':
        """
        Compose context for arguments

        :param args: Arguments
        :return: Context
        """
        namespace = self.delegate.parse_args(args)

        return Context(
            action=Action(namespace.action),
            dry_run=namespace.dry_run,
            verbose=namespace.verbose,
        )

    def options(self):
        """
        Returns all available options

        :return: List of available options
        """

        # pylint: disable=protected-access
        return self.delegate._optionals._group_actions


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
        timber.bootstrap()

        # context
        parser = ContextParser()
        context = parser.parse(args)

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
            PrefInstallAction(noop=noop, logger=logger),
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
            PrefUninstallAction(noop=noop, logger=logger),
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
        identity = Identity.detect()

        commands = []

        if identity.is_linux():
            commands.extend([])

        if identity.is_darwin():
            commands.extend([
                BrewInstallAction(noop=noop, logger=logger),
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
            BrewUninstallAction(noop=noop, logger=logger),
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
            PrefStatusAction(noop=noop, logger=logger),
            BrewStatusAction(noop=noop, logger=logger),
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

        parser = ContextParser()

        template = Template(
            filename=Completion.SOURCE,
            input_encoding="utf-8",
            output_encoding="utf-8",
            bytestring_passthrough=True,
        )

        rendered = template.render(
            options=parser.options(),
            actions=[x.value for x in Action],
        )

        with open(Completion.DESTINATION, 'w') as dst:
            dst.write(rendered)

        sys.stdout.write(rendered)
        return
