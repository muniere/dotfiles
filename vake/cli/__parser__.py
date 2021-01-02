import sys
import argparse

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
        parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog, width=240))
        parser.add_argument("-n", "--dry-run", dest="dry_run", action="store_true", help="Do not execute commands actually")
        parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="Show verbose messages")
        parser.add_argument("action", type=str, help="Action to perform: (%s)" % "|".join(Action.values()))
        parser.add_argument("target", type=str, nargs="*", help="Target for action: (%s)" % "|".join(Target.values()))

        namespace = parser.parse_args(args)

        context = Context()
        context.action = namespace.action
        context.targets = namespace.target or ["dotfile", "binfile"]
        context.dry_run = namespace.dry_run
        context.verbose = namespace.verbose

        return context
