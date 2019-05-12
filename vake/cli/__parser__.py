import sys

from .__action__ import Action
from .__target__ import Target
from .__context__ import Context

class Parser:

    @classmethod
    def parse(cls, args):
        """
        Compose context for arguments

        :param args: Arguments
        :return: Context
        """
        if sys.version_info >= (2, 7, 0):
            return cls.__parse_argparse(args)
        else:
            return cls.__parse_optparse(args)

    @classmethod
    def options(cls):
        """
        Get possible options
        """
        if sys.version_info >= (2, 7, 0):
            return cls.__make_argparser()._optionals._group_actions
        else:
            return list()

    @classmethod
    def __parse_argparse(cls, args):
        parser = cls.__make_argparser()

        namespace = parser.parse_args(args)

        context = Context()
        context.action = namespace.action
        context.targets = namespace.target or ["dotfile", "binfile"]
        context.dry_run = namespace.dry_run
        context.verbose = namespace.verbose

        return context

    @classmethod
    def __parse_optparse(cls, args):
        parser = cls.__make_optparser()

        (opts, argv) = parser.parse_args(args)

        context = Context()
        context.action = argv[0]
        context.targets = argv[1:] or ["dotfile", "binfile"]
        context.dry_run = opts.dry_run
        context.verbose = opts.verbose

        return context

    @classmethod
    def __make_argparser(cls):
        import argparse

        parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog, width=240))
        parser.add_argument("-n", "--dry-run", dest="dry_run", action="store_true", help="Do not execute commands actually")
        parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="Show verbose messages")
        parser.add_argument("action", type=str, help="Action to perform: (%s)" % "|".join(Action.values()))
        parser.add_argument("target", type=str, nargs="*", help="Target for action: (%s)" % "|".join(Target.values()))

        return parser

    @classmethod
    def __make_optparser(cls):
        import optparse

        parser = optparse.OptionParser(usage="Usage: %prog [options] <command> [<target> ...]")
        parser.add_option("-n", "--dry-run", dest="dry_run", action="store_true", help="Do not execute commands actually")
        parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="Show verbose messages")

        return parser
