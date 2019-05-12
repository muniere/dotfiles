# 1st
import sys

# 2nd
from .. import winston
from .__parser__ import Parser
from .__action__ import Action
from .__target__ import Target
from .__completion__ import Completion


def cli():
    return CLI()


class CLI:
    """
    CLI launcher
    """

    def __init__(self):
        """
        Initialize application
        """
        pass

    def run(self, args):
        """
        Run application
        """
        # logging
        winston.bootstrap()

        # context
        context = Parser.parse(args)

        # completion
        if context.action == Action.COMPLETION:
            self.completion(context)
            sys.exit(0)

        # action
        for command in context.commands():
            command.run()

        sys.exit(0)

    def completion(self, context):
        """
        Show messages for completion

        :param context: Context
        """

        from mako.template import Template

        template = Template(
            filename=Completion.SOURCE,
            input_encoding="utf-8",
            output_encoding="utf-8"
        )

        rendered = template.render(
            options=Parser.options(),
            actions=Action.values(),
            targets=Target.values(),
        )

        with open(Completion.DESTINATION, 'w') as dst:
            dst.write(rendered)

        sys.stdout.write(rendered)
        return
