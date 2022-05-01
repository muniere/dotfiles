import abc
import argparse
import builtins
import sys
from abc import abstractmethod
from argparse import ArgumentParser, ArgumentError, Namespace
from dataclasses import dataclass
from pathlib import Path
from typing import List

from . import _
from . import kernel
from . import timber
from .intent import Action, PrefListColorOption, PrefListStyleOption
from .intent import PrefLinkAction, PrefUnlinkAction, PrefCleanupAction, PrefListAction
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
        stream = sys.stdout

        level = _.box(verbose).fold(
            some=lambda: Level.DEBUG,
            none=lambda: Level.TRACE
        )

        formatter = _.box(stream.isatty()).fold(
            some=lambda: TaggedFormatter.colored(),
            none=lambda: TaggedFormatter.default(),
        )

        handler = StreamHandler(stream=stream)
        handler.set_level(level)
        handler.set_formatter(formatter)

        logger = timber.get_logger(__name__)
        logger.set_level(level)
        logger.add_handler(handler)

        return logger

    class Factory(metaclass=abc.ABCMeta):

        # noinspection PyUnresolvedReferences,PyProtectedMember
        @classmethod
        @abstractmethod
        def register(cls, subparsers: argparse._SubParsersAction):
            raise NotImplementedError()

        @abstractmethod
        def create(self, args: Namespace) -> 'Command':
            raise NotImplementedError()


@dataclass(frozen=True)
class ListCommand(Command):
    NAME = 'list'

    long: bool
    color: str

    def run(self):
        identity = kernel.identify()

        actions: List[Action] = [
            PrefListAction(
                color=PrefListColorOption(self.color),
                style=PrefListStyleOption.LONG if self.long else PrefListStyleOption.SHORT,
            ),
        ]

        if identity.is_linux():
            actions += []

        if identity.is_darwin():
            actions += []

        for action in actions:
            action.run()

        return

    class Factory(Command.Factory):

        # noinspection PyUnresolvedReferences,PyProtectedMember
        @classmethod
        def register(cls, subparsers: argparse._SubParsersAction):
            child = subparsers.add_parser(ListCommand.NAME)
            child.set_defaults(factory=cls())
            child.add_argument(
                '-l', '--long',
                dest='long',
                action='store_true',
                help='Show in long format'
            )
            child.add_argument(
                '--color',
                dest='color',
                choices=['auto', 'always', 'never'],
                default='auto',
                help='Choose how to colorize output'
            )

        def create(self, args: Namespace) -> Command:
            return ListCommand(
                long=args.long,
                color=args.color,
            )


@dataclass(frozen=True)
class LinkCommand(Command):
    NAME = 'link'

    cleanup: bool
    activate: bool
    dry_run: bool
    verbose: bool

    def run(self):
        cleanup = self.cleanup
        activate = self.activate
        noop = self.dry_run
        logger = self._logger(verbose=self.verbose)

        actions = [
            PrefLinkAction(cleanup=cleanup, activate=activate, noop=noop, logger=logger),
        ]

        for action in actions:
            action.run()

        return

    class Factory(Command.Factory):

        # noinspection PyUnresolvedReferences,PyProtectedMember
        @classmethod
        def register(cls, subparsers: argparse._SubParsersAction):
            child = subparsers.add_parser(LinkCommand.NAME)
            child.set_defaults(factory=cls())
            child.add_argument(
                '--skip-cleanup',
                dest='skip_cleanup',
                action='store_true',
                help='Skip cleanup action before link'
            )
            child.add_argument(
                '--skip-activate',
                dest='skip_activate',
                action='store_true',
                help='Skip activation after each link'
            )
            child.add_argument(
                '-n', '--dry-run',
                dest='dry_run',
                action='store_true',
                help='Do not execute commands actually'
            )
            child.add_argument(
                '-v', '--verbose',
                dest='verbose',
                action='store_true',
                help='Show verbose messages'
            )

        def create(self, args: Namespace) -> Command:
            return LinkCommand(
                cleanup=not args.skip_cleanup,
                activate=not args.skip_activate,
                dry_run=args.dry_run,
                verbose=args.verbose,
            )


@dataclass(frozen=True)
class UnlinkCommand(Command):
    NAME = 'unlink'

    cleanup: bool
    deactivate: bool
    dry_run: bool
    verbose: bool

    def run(self) -> None:
        cleanup = self.cleanup
        deactivate = self.deactivate
        noop = self.dry_run
        logger = self._logger(verbose=self.verbose)

        actions = [
            PrefUnlinkAction(cleanup=cleanup, deactivate=deactivate, noop=noop, logger=logger),
        ]

        for action in actions:
            action.run()

        return

    class Factory(Command.Factory):

        # noinspection PyUnresolvedReferences,PyProtectedMember
        @classmethod
        def register(cls, subparsers: argparse._SubParsersAction):
            child = subparsers.add_parser(UnlinkCommand.NAME)
            child.set_defaults(factory=cls())
            child.add_argument(
                '--skip-cleanup',
                dest='skip_cleanup',
                action='store_true',
                help='Skip cleanup action before unlink'
            )
            child.add_argument(
                '--skip-deactivate',
                dest='skip_deactivate',
                action='store_true',
                help='Skip deactivation after each unlink'
            )
            child.add_argument(
                '-n', '--dry-run',
                dest='dry_run',
                action='store_true',
                help='Do not execute commands actually'
            )
            child.add_argument(
                '-v', '--verbose',
                dest='verbose',
                action='store_true',
                help='Show verbose messages'
            )

        def create(self, args: Namespace) -> Command:
            return UnlinkCommand(
                cleanup=not args.skip_cleanup,
                deactivate=not args.skip_deactivate,
                dry_run=args.dry_run,
                verbose=args.verbose,
            )


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

    class Factory(Command.Factory):

        # noinspection PyUnresolvedReferences,PyProtectedMember
        @classmethod
        def register(cls, subparsers: argparse._SubParsersAction):
            child = subparsers.add_parser(CleanupCommand.NAME)
            child.set_defaults(factory=cls())
            child.add_argument(
                '-n', '--dry-run',
                dest='dry_run',
                action='store_true',
                help='Do not execute commands actually'
            )
            child.add_argument(
                '-v', '--verbose',
                dest='verbose',
                action='store_true',
                help='Show verbose messages'
            )

        def create(self, args: Namespace) -> Command:
            return CleanupCommand(
                dry_run=args.dry_run,
                verbose=args.verbose,
            )


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
            # TODO: uncomment after upgraded to python 3.9
            # bytestring_passthrough=True,
        )

        rendered = template.render(
            options=parser.options,
            actions=parser.actions,
        )

        dst.write_text(rendered, encoding='utf-8')

        sys.stdout.write(rendered)
        return

    class Factory(Command.Factory):

        # noinspection PyUnresolvedReferences,PyProtectedMember
        @classmethod
        def register(cls, subparsers: argparse._SubParsersAction):
            child = subparsers.add_parser(CompletionCommand.NAME)
            child.set_defaults(factory=cls())

        def create(self, args: Namespace) -> Command:
            return CompletionCommand()


class CommandParser:
    __delegate: ArgumentParser

    def __init__(self):
        parser = ArgumentParser(
            # TODO: uncomment after upgraded to python 3.9
            # exit_on_error=False
        )
        subparsers = parser.add_subparsers()
        ListCommand.Factory.register(subparsers)
        LinkCommand.Factory.register(subparsers)
        UnlinkCommand.Factory.register(subparsers)
        CleanupCommand.Factory.register(subparsers)
        CompletionCommand.Factory.register(subparsers)

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

    def parse(self, args: List[str]) -> Command:
        args = self.__delegate.parse_args(args)

        if hasattr(args, 'factory'):
            factory: Command.Factory = args.factory
            return factory.create(args)
        else:
            raise ArgumentError(argument=None, message='unknown command')

    def print_help(self):
        self.__delegate.print_help()

    def format_help(self) -> str:
        return self.__delegate.format_help()


def run(args: List[str]) -> None:
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
