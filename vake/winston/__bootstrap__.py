import logging

from . import __level__ as level

def __execute(self, cmd, *args, **kwargs):
    """
    Log 'msg % args' with severity 'EXEC'.

    To pass exception information, use the keyword argument exc_info with
    a true value, e.g.

    logger.execute("Houston, we have a %s", "interesting problem", exc_info=1)
    """
    if self.isEnabledFor(level.EXEC):
        self._log(level.EXEC, cmd, args, **kwargs)
    return

def run():
    logging.Logger.execute = __execute
