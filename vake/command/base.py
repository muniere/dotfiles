# 3rd
from .. import shell

# interface
class Action:
    def __init__(self, noop=False, logger=None):

        self.noop = noop
        self.logger = logger

        self.shell = shell.Client()
        self.shell.noop = noop
        self.shell.logger = logger

        return

    def run(self):
        pass
