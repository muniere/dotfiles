import abc
import argparse
import builtins
import sys
from abc import abstractmethod
from argparse import ArgumentParser, ArgumentError
from dataclasses import dataclass
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


class Command(metaclass=abc.ABCMeta):
    @classmethod
    @abstractmethod
    def name(cls):
        return NotImplementedError

    @staticmethod
    def _logger(verbose: bool) -> Lumber:
        if verbose:
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


@dataclass(frozen=True)
class ListCommand(Command):
    @classmethod
    def name(cls):
        return 'list'

    long: bool


@dataclass(frozen=True)
class LinkCommand(Command):
    @classmethod
    def name(cls):
        return 'link'

    dry_run: bool
    verbose: bool

    def logger(self) -> Lumber:
        return self._logger(verbose=self.verbose)


@dataclass(frozen=True)
class UnlinkCommand(Command):
    @classmethod
    def name(cls):
        return 'unlink'

    dry_run: bool
    verbose: bool

    def logger(self) -> Lumber:
        return self._logger(verbose=self.verbose)


@dataclass(frozen=True)
class InstallCommand(Command):
    @classmethod
    def name(cls):
        return 'install'

    dry_run: bool
    verbose: bool

    def logger(self) -> Lumber:
        return self._logger(verbose=self.verbose)


@dataclass(frozen=True)
class UninstallCommand(Command):
    @classmethod
    def name(cls):
        return 'uninstall'

    dry_run: bool
    verbose: bool

    def logger(self) -> Lumber:
        return self._logger(verbose=self.verbose)


@dataclass(frozen=True)
class CompletionCommand(Command):
    @classmethod
    def name(cls):
        return 'completion'

    @property
    def src(self) -> Path:
        return Path('template/_xake')

    @property
    def dst(self) -> Path:
        return Path('static/default/zsh-completions/_xake')


class CommandParser:
    __delegate: ArgumentParser

    def __init__(self):
        parser = ArgumentParser(exit_on_error=False)

        subparsers = parser.add_subparsers()

        list_parser = subparsers.add_parser(ListCommand.name())
        list_parser.set_defaults(command=ListCommand.name())
        list_parser.add_argument(
            '-l', '--long',
            dest='long',
            action='store_true',
            help='Show in long format'
        )

        completion_parser = subparsers.add_parser(CompletionCommand.name())
        completion_parser.set_defaults(command=CompletionCommand.name())

        for cmd in [LinkCommand, UnlinkCommand, InstallCommand, UninstallCommand]:
            child_parser = subparsers.add_parser(cmd.name())
            child_parser.set_defaults(command=cmd.name())
            child_parser.add_argument(
                '-n', '--dry-run',
                dest='dry_run',
                action='store_true',
                help='Do not execute commands actually'
            )
            child_parser.add_argument(
                '-v', '--verbose',
                dest='verbose',
                action='store_true',
                help='Show verbose messages'
            )

        self.__delegate = parser

    # noinspection PyUnresolvedReferences,PyProtectedMember
    @property
    def actions(self):
        # pylint: disable=protected-access
        for action in self.__delegate._subparsers._actions:
            if isinstance(action, argparse._SubParsersAction):
                return list(action.choices.keys())
        # pylint: enable=protected-access

        return []

    # noinspection PyUnresolvedReferences,PyProtectedMember
    @property
    def options(self):
        # pylint: disable=protected-access
        return self.__delegate._optionals._group_actions
        # pylint: enable=protected-access

    def parse(self, args: list[str]) -> Command:
        namespace = self.__delegate.parse_args(args)

        if not hasattr(namespace, 'command'):
            raise ArgumentError(argument=None, message='no subcommand given')

        command_s: str = namespace.command

        if command_s == ListCommand.name():
            return ListCommand(
                long=namespace.long,
            )

        if command_s == LinkCommand.name():
            return LinkCommand(
                dry_run=namespace.dry_run,
                verbose=namespace.verbose,
            )

        if command_s == UnlinkCommand.name():
            return UnlinkCommand(
                dry_run=namespace.dry_run,
                verbose=namespace.verbose,
            )

        elif command_s == InstallCommand.name():
            return InstallCommand(
                dry_run=namespace.dry_run,
                verbose=namespace.verbose,
            )

        if command_s == UninstallCommand.name():
            return UninstallCommand(
                dry_run=namespace.dry_run,
                verbose=namespace.verbose,
            )

        if command_s == CompletionCommand.name():
            return CompletionCommand()

        raise ArgumentError(argument=None, message=f'unknown command: {command_s}')

    def print_help(self):
        self.__delegate.print_help()

    def format_help(self) -> str:
        return self.__delegate.format_help()


def run(args: list[str]) -> None:
    """
    Run application with given arguments.

    :param args: CLI arguments
    """

    # logging
    timber.bootstrap()

    # context
    parser = CommandParser()

    try:
        command = parser.parse(args)
    except ArgumentError as err:
        builtins.print(err, file=sys.stderr)
        builtins.print(file=sys.stderr)
        sys.exit(parser.format_help())

    # commands
    if isinstance(command, ListCommand):
        __list(command)
        sys.exit(0)

    if isinstance(command, LinkCommand):
        __link(command)
        sys.exit(0)

    if isinstance(command, UnlinkCommand):
        __unlink(command)
        sys.exit(0)

    if isinstance(command, InstallCommand):
        __install(command)
        sys.exit(0)

    if isinstance(command, UninstallCommand):
        __uninstall(command)
        sys.exit(0)

    if isinstance(command, CompletionCommand):
        __completion(command)
        sys.exit(0)

    sys.exit(1)


def __list(command: ListCommand) -> None:
    identity = kernel.identify()

    actions: list[Action] = [
        PrefListAction(long=command.long),
    ]

    if identity.is_linux():
        actions += []

    if identity.is_darwin():
        actions += []

    for action in actions:
        action.run()

    return


def __link(command: LinkCommand) -> None:
    noop = command.dry_run
    logger = command.logger()

    actions = [
        PrefInstallAction(noop=noop, logger=logger),
    ]

    for action in actions:
        action.run()

    return


def __unlink(command: UnlinkCommand) -> None:
    noop = command.dry_run
    logger = command.logger()

    actions = [
        PrefUninstallAction(noop=noop, logger=logger),
    ]

    for action in actions:
        action.run()

    return


def __install(command: InstallCommand) -> None:
    noop = command.dry_run
    logger = command.logger()
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


def __uninstall(command: UninstallCommand) -> None:
    noop = command.dry_run
    logger = command.logger()
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


def __completion(command: CompletionCommand) -> None:
    # pylint: disable=import-outside-toplevel
    from mako.template import Template

    parser = CommandParser()
    src = command.src
    dst = command.dst

    template = Template(
        filename=str(src),
        input_encoding='utf-8',
        output_encoding='utf-8',
        bytestring_passthrough=True,
    )

    rendered = template.render(
        options=parser.options,
        actions=parser.actions,
    )

    dst.write_text(rendered, encoding='utf-8')

    sys.stdout.write(rendered)
    return
