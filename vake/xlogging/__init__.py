"""
Extend package of standard logging package
"""

# 0th
from logging import *

#
# Constants
#
DEBUG = 10
INFO = 20
EXEC = 25
WARN = 30
ERROR = 40

#
# Refine levels
#
addLevelName(DEBUG, "DEBUG")
addLevelName(INFO, "INFO")
addLevelName(EXEC, "EXEC")
addLevelName(WARN, "WARN")
addLevelName(ERROR, "ERROR")

#
# Functions
#
def __execute(self, cmd, *args, **kwargs):
    """
    Log 'msg % args' with severity 'EXEC'.

    To pass exception information, use the keyword argument exc_info with
    a true value, e.g.

    logger.execute("Houston, we have a %s", "interesting problem", exc_info=1)
    """
    if self.isEnabledFor(EXEC):
        self._log(EXEC, cmd, args, **kwargs)
    return


Logger.execute = __execute

#
# Classes
#
class LabelFormatter(Formatter):
    LEVEL_NAME_WIDTH = 5

    def format(self, record):
        message = "[%s] %s" % (record.levelname.ljust(self.__class__.LEVEL_NAME_WIDTH), record.getMessage())
        return self.colorize(message, levelno=record.levelno)

    @staticmethod
    def colorize(message, levelno=NOTSET):
        reset_str = "\033[0m"

        color_dict = {
            DEBUG: "\033[32m", # green
            INFO: "\033[36m",  # cyan
            EXEC: "\033[35m",  # magenta
            WARN: "\033[33m",  # yellow
            ERROR: "\033[33m", # red
        }

        if levelno in color_dict:
            color_str = color_dict[levelno]
        else:
            color_str = reset_str

        return "%s%s%s" % (color_str, message, reset_str)
