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
            noop = self.dry_run
            logger = self.__make_logger()

            concerns = [Concern.hunt(t) for t in self.targets]
            concerns = [x for x in concerns if Concern.installable(x)]

            return [x.Install(noop=noop, logger=logger) for x in concerns]

        if self.action == Action.UNINSTALL:
            noop = self.dry_run
            logger = self.__make_logger()

            concerns = [Concern.hunt(t) for t in self.targets]
            concerns = [x for x in concerns if Concern.uninstallable(x)]

            return [x.Uninstall(noop=noop, logger=logger) for x in concerns]

        if self.action == Action.STATUS:
            noop = self.dry_run
            logger = self.__make_logger()

            concerns = [Concern.hunt(t) for t in self.targets]
            concerns = [x for x in concerns if Concern.statusable(x)]

            return [x.Status(noop=noop, logger=logger) for x in concerns]

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
