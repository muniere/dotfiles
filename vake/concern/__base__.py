# 1st
from abc import ABCMeta, abstractmethod

# 2nd
from .. import kernel


class Action(metaclass=ABCMeta):

    def __init__(self, noop=False, logger=None):
        self.noop = noop
        self.logger = logger
        self.shell = kernel.shell(noop, logger)
        return

    @abstractmethod
    def run(self):
        pass
