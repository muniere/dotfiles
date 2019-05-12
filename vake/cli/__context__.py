from .. import winston
from .__action__ import Action
from .__concern__ import Concern

class Context:
    """
    Attributes store for application
    """
    def __init__(self):
        """
        Initialize context
        """
        self.action = None
        self.targets = []
        self.dry_run = False
        self.verbose = False
        return

    def commands(self):
        if self.action == Action.INSTALL:
            logger = self.__make_logger()
            concerns = [m for m in [Concern.hunt(t) for t in self.targets]]
            concerns = [m for m in concerns if m is not None and m.Install is not None]
            commands = [m.Install(noop=self.dry_run, logger=logger) for m in concerns]
            commands = [c for c in commands if c is not None]
            return commands

        if self.action == Action.UNINSTALL:
            logger = self.__make_logger()
            concerns = [m for m in [Concern.hunt(t) for t in self.targets]]
            concerns = [m for m in concerns if m is not None and m.Uninstall is not None]
            commands = [m.Uninstall(noop=self.dry_run, logger=logger) for m in concerns]
            commands = [c for c in commands if c is not None]
            return commands

        if self.action == Action.STATUS:
            logger = self.__make_logger()
            concerns = [m for m in [Concern.hunt(t) for t in self.targets]]
            concerns = [m for m in concerns if m is not None and m.Status is not None]
            commands = [m.Status(noop=self.dry_run, logger=logger) for m in concerns]
            commands = [c for c in commands if c is not None]
            return commands

        return []

    def __make_logger(self):
        if self.verbose:
            level = winston.DEBUG
        else:
            level = winston.EXEC

        formatter = winston.LabelFormatter()

        handler = winston.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(formatter)

        logger = winston.getLogger(__name__)
        logger.setLevel(level)
        logger.addHandler(handler)

        return logger
