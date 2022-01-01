import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from . import kernel
from . import timber
from .intent import BrewInstallAction, BrewUninstallAction, BrewStatusAction
from .intent import PrefInstallAction, PrefUninstallAction, PrefStatusAction
from .timber import Level, ColoredFormatter, StreamHandler, Lumber

__all__ = [
    'Application'
]


class Command(Enum):
    LINK = 'link'
    UNLINK = 'unlink'
    INSTALL = 'install'
    UNINSTALL = 'uninstall'
    STATUS = 'status'
    COMPLETION = 'completion'


class Locator:
    @staticmethod
    def completion_src() -> Path:
        return Path('template/_xake')

    @staticmethod
    def completion_dst() -> Path:
        return Path('static/default/zsh-completions/_xake')


@dataclass(frozen=True)
class Context:
    command: Command
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
        commands = '|'.join([x.value for x in Command])

        self.delegate = ArgumentParser()
        self.delegate.add_argument('-n', '--dry-run',
                                   dest='dry_run',
                                   action='store_true',
                                   help='Do not execute commands actually')
        self.delegate.add_argument('-v', '--verbose',
                                   dest='verbose',
                                   action='store_true',
                                   help='Show verbose messages')
        self.delegate.add_argument('command',
                                   type=str,
                                   help=f'Command to perform: ({commands})')

    def parse(self, args: list[str]) -> 'Context':
        """
        Compose context for arguments

        :param args: Arguments
        :return: Context
        """
        namespace = self.delegate.parse_args(args)

        return Context(
            command=Command(namespace.command),
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


class Application:
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
        timber.bootstrap()

        # context
        parser = ContextParser()
        context = parser.parse(args)

        # commands
        if context.command == Command.LINK:
            self.__deploy(context)
            sys.exit(0)

        if context.command == Command.UNLINK:
            self.__undeploy(context)
            sys.exit(0)

        if context.command == Command.INSTALL:
            self.__install(context)
            sys.exit(0)

        if context.command == Command.UNINSTALL:
            self.__uninstall(context)
            sys.exit(0)

        if context.command == Command.STATUS:
            self.__status(context)
            sys.exit(0)

        if context.command == Command.COMPLETION:
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

        actions = [
            PrefInstallAction(noop=noop, logger=logger),
        ]

        for action in actions:
            action.run()

        return

    @staticmethod
    def __undeploy(context: Context) -> None:
        """
        Perform untine action.

        :param context: Context
        """
        noop = context.dry_run
        logger = context.logger()

        actions = [
            PrefUninstallAction(noop=noop, logger=logger),
        ]

        for action in actions:
            action.run()

        return

    @staticmethod
    def __install(context: Context) -> None:
        """
        Perform install action.

        :param context: Context
        """

        noop = context.dry_run
        logger = context.logger()
        identity = kernel.identify()

        actions = []

        if identity.is_linux():
            actions += []

        if identity.is_darwin():
            actions += [
                BrewInstallAction(noop=noop, logger=logger),
            ]

        for action in actions:
            action.run()

        return

    @staticmethod
    def __uninstall(context: Context) -> None:
        """
        Perform uninstall action.

        :param context: Context
        """
        noop = context.dry_run
        logger = context.logger()

        actions = [
            BrewUninstallAction(noop=noop, logger=logger),
        ]

        for action in actions:
            action.run()

        return

    @staticmethod
    def __status(context: Context) -> None:
        """
        Perform status action.

        :param context: Context
        """
        noop = context.dry_run
        logger = context.logger()

        actions = [
            PrefStatusAction(noop=noop, logger=logger),
            BrewStatusAction(noop=noop, logger=logger),
        ]

        for action in actions:
            action.run()

        return

    @staticmethod
    def __completion() -> None:
        """
        Perform completion action.
        """

        # pylint: disable=import-outside-toplevel
        from mako.template import Template

        parser = ContextParser()
        src = Locator.completion_src()
        dst = Locator.completion_dst()

        template = Template(
            filename=str(src),
            input_encoding='utf-8',
            output_encoding='utf-8',
            bytestring_passthrough=True,
        )

        rendered = template.render(
            options=parser.options(),
            actions=[x.value for x in Command],
        )

        dst.write_text(rendered, encoding='utf-8')

        sys.stdout.write(rendered)
        return
