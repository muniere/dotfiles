import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from . import kernel
from . import timber
from .intent import Action
from .intent import BrewInstallAction, BrewUninstallAction
from .intent import PrefInstallAction, PrefUninstallAction, PrefListAction
from .timber import Level, TaggedFormatter, StreamHandler, Lumber

__all__ = [
    'run'
]


class Command(Enum):
    LIST = 'list'
    LINK = 'link'
    UNLINK = 'unlink'
    INSTALL = 'install'
    UNINSTALL = 'uninstall'
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

        stream = sys.stdout

        if stream.isatty():
            formatter = TaggedFormatter.colored()
        else:
            formatter = TaggedFormatter.default()

        handler = StreamHandler(stream=stream)
        handler.set_level(level)
        handler.set_formatter(formatter)

        logger = timber.get_logger(__name__)
        logger.set_level(level)
        logger.add_handler(handler)

        return logger


class ContextParser:
    __delegate: ArgumentParser

    def __init__(self):
        commands = '|'.join([x.value for x in Command])

        parser = ArgumentParser()
        parser.add_argument(
            '-n', '--dry-run',
            dest='dry_run',
            action='store_true',
            help='Do not execute commands actually'
        )
        parser.add_argument(
            '-v', '--verbose',
            dest='verbose',
            action='store_true',
            help='Show verbose messages'
        )
        parser.add_argument(
            'command',
            type=str,
            help=f'Command to perform: ({commands})'
        )

        self.__delegate = parser

    def parse(self, args: list[str]) -> 'Context':
        """
        Compose context for arguments

        :param args: Arguments
        :return: Context
        """
        namespace = self.__delegate.parse_args(args)

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
        return self.__delegate._optionals._group_actions


def run(args: list[str]) -> None:
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
    if context.command == Command.LIST:
        __list(context)
        sys.exit(0)

    if context.command == Command.LINK:
        __link(context)
        sys.exit(0)

    if context.command == Command.UNLINK:
        __unlink(context)
        sys.exit(0)

    if context.command == Command.INSTALL:
        __install(context)
        sys.exit(0)

    if context.command == Command.UNINSTALL:
        __uninstall(context)
        sys.exit(0)

    if context.command == Command.COMPLETION:
        __completion()
        sys.exit(0)

    sys.exit(1)


def __list(context: Context) -> None:
    noop = context.dry_run
    logger = context.logger()
    identity = kernel.identify()

    actions: list[Action] = [
        PrefListAction(noop=noop, logger=logger),
    ]

    if identity.is_linux():
        actions += []

    if identity.is_darwin():
        actions += []

    for action in actions:
        action.run()

    return


def __link(context: Context) -> None:
    noop = context.dry_run
    logger = context.logger()

    actions = [
        PrefInstallAction(noop=noop, logger=logger),
    ]

    for action in actions:
        action.run()

    return


def __unlink(context: Context) -> None:
    noop = context.dry_run
    logger = context.logger()

    actions = [
        PrefUninstallAction(noop=noop, logger=logger),
    ]

    for action in actions:
        action.run()

    return


def __install(context: Context) -> None:
    noop = context.dry_run
    logger = context.logger()
    identity = kernel.identify()

    actions: list[Action] = []

    if identity.is_linux():
        actions += []

    if identity.is_darwin():
        actions += [
            BrewInstallAction(noop=noop, logger=logger),
        ]

    for action in actions:
        action.run()

    return


def __uninstall(context: Context) -> None:
    noop = context.dry_run
    logger = context.logger()
    identity = kernel.identify()

    actions: list[Action] = []

    if identity.is_linux():
        actions += []

    if identity.is_darwin():
        actions += [
            BrewUninstallAction(noop=noop, logger=logger),
        ]

    for action in actions:
        action.run()

    return


def __completion() -> None:
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
