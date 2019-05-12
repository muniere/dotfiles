import logging

from . import __level__ as level

class LabelFormatter(logging.Formatter):
    LEVEL_NAME_WIDTH = 5

    def format(self, record):
        message = "[%s] %s" % (record.levelname.ljust(
            self.__class__.LEVEL_NAME_WIDTH), record.getMessage())
        return self.colorize(message, levelno=record.levelno)

    @staticmethod
    def colorize(message, levelno=logging.NOTSET):
        reset_str = "\033[0m"

        color_dict = {
            level.DEBUG: "\033[32m",  # green
            level.EXEC: "\033[35m",  # magenta
            level.INFO: "\033[36m",  # cyan
            level.WARN: "\033[33m",  # yellow
            level.ERROR: "\033[33m",  # red
        }

        if levelno in color_dict:
            color_str = color_dict[levelno]
        else:
            color_str = reset_str

        return "%s%s%s" % (color_str, message, reset_str)
