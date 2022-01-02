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
from .intent import PrefInstallAction, PrefUninstallAction, PrefCleanupAction, PrefListAction
from .timber import Level, TaggedFormatter, StreamHandler, Lumber

__all__ = [
    'run'
]


class Command(metaclass=abc.ABCMeta):
    @abstractmethod
    def run(self):
        raise NotImplementedError()

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
    NAME = 'list'

    long: bool

    def run(self):
        identity = kernel.identify()

        actions: list[Action] = [
            PrefListAction(long=self.long),
        ]

        if identity.is_linux():
            actions += []

        if identity.is_darwin():
            actions += []

        for action in actions:
            action.run()

        return


@dataclass(frozen=True)
class LinkCommand(Command):
    NAME = 'link'

    dry_run: bool
    verbose: bool

    def run(self):
        noop = self.dry_run
        logger = self._logger(verbose=self.verbose)

        actions = [
            PrefInstallAction(noop=noop, logger=logger),
        ]

        for action in actions:
            action.run()

        return


@dataclass(frozen=True)
class UnlinkCommand(Command):
    NAME = 'unlink'

    dry_run: bool
    verbose: bool

    def run(self) -> None:
        noop = self.dry_run
        logger = self._logger(verbose=self.verbose)

        actions = [
            PrefUninstallAction(noop=noop, logger=logger),
        ]

        for action in actions:
            action.run()

        return


@dataclass(frozen=True)
class CleanupCommand(Command):
    NAME = 'cleanup'

    dry_run: bool
    verbose: bool

    def run(self) -> None:
        noop = self.dry_run
        logger = self._logger(verbose=self.verbose)

        actions = [
            PrefCleanupAction(noop=noop, logger=logger),
        ]

        for action in actions:
            action.run()

        return


@dataclass(frozen=True)
class CompletionCommand(Command):
    NAME = 'completion'

    @property
    def src(self) -> Path:
        return Path('template/_xake')

    @property
    def dst(self) -> Path:
        return Path('static/default/zsh-completions/_xake')

    def run(self) -> None:
        # pylint: disable=import-outside-toplevel
        from mako.template import Template

        parser = CommandParser()
        src = self.src
        dst = self.dst

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


class CommandParser:
    __delegate: ArgumentParser

    def __init__(self):
        parser = ArgumentParser(exit_on_error=False)

        subparsers = parser.add_subparsers()

        list_parser = subparsers.add_parser(ListCommand.NAME)
        list_parser.set_defaults(command=ListCommand.NAME)
        list_parser.add_argument(
            '-l', '--long',
            dest='long',
            action='store_true',
            help='Show in long format'
        )

        completion_parser = subparsers.add_parser(CompletionCommand.NAME)
        completion_parser.set_defaults(command=CompletionCommand.NAME)

        for command in [LinkCommand.NAME, UnlinkCommand.NAME, CleanupCommand.NAME]:
            child_parser = subparsers.add_parser(command)
            child_parser.set_defaults(command=command)
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

        if command_s == ListCommand.NAME:
            return ListCommand(
                long=namespace.long,
            )

        if command_s == LinkCommand.NAME:
            return LinkCommand(
                dry_run=namespace.dry_run,
                verbose=namespace.verbose,
            )

        if command_s == UnlinkCommand.NAME:
            return UnlinkCommand(
                dry_run=namespace.dry_run,
                verbose=namespace.verbose,
            )

        if command_s == CleanupCommand.NAME:
            return CleanupCommand(
                dry_run=namespace.dry_run,
                verbose=namespace.verbose,
            )

        if command_s == CompletionCommand.NAME:
            return CompletionCommand()

        raise ArgumentError(argument=None, message=f'unknown command: {command_s}')

    def print_help(self):
        self.__delegate.print_help()

    def format_help(self) -> str:
        return self.__delegate.format_help()


def run(args: list[str]) -> None:
    timber.bootstrap()

    parser = CommandParser()

    try:
        command = parser.parse(args)
        command.run()
        sys.exit(0)
    except ArgumentError as err:
        builtins.print(err, file=sys.stderr)
        builtins.print(file=sys.stderr)
        sys.exit(parser.format_help())
