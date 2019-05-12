from .. import kernel


class Action:

    def __init__(self, noop=False, logger=None):
        self.noop = noop
        self.logger = logger
        self.shell = kernel.shell(noop, logger)
        return

    def run(self):
        pass
