import logging

from typing import Optional

__all__ = [
    'DEBUG', 'EXEC', 'INFO', 'WARN', 'ERROR',
    'ColoredFormatter', 'StreamHandler', 'LoggerWrapper',
    'bootstrap', 'get_logger',
]

DEBUG = 10
EXEC = 15
INFO = 20
WARN = 30
ERROR = 40


class ColoredFormatter(logging.Formatter):
    LEVEL_NAME_WIDTH = 5

    def format(self, record: logging.LogRecord):
        message = "[%s] %s" % (
            record.levelname.ljust(self.__class__.LEVEL_NAME_WIDTH),
            record.getMessage(),
        )
        return self.colorize(message, levelno=record.levelno)

    @staticmethod
    def colorize(message, levelno=logging.NOTSET):
        reset_str = "\033[0m"

        color_dict = {
            DEBUG: "\033[32m",  # green
            EXEC: "\033[35m",  # magenta
            INFO: "\033[36m",  # cyan
            WARN: "\033[33m",  # yellow
            ERROR: "\033[33m",  # red
        }

        color_str = color_dict.get(levelno, reset_str)

        return "%s%s%s" % (color_str, message, reset_str)


class StreamHandler(logging.StreamHandler):

    def set_level(self, level: int):
        self.setLevel(level)

    def set_formatter(self, formatter: ColoredFormatter):
        self.setFormatter(formatter)


class LoggerWrapper:

    def __init__(self, delegate: logging.Logger):
        self._delegate = delegate

    def debug(self, msg, *args, **kwargs):
        self._delegate.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._delegate.info(msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        self._delegate.warning(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._delegate.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._delegate.error(msg, *args, **kwargs)

    def execute(self, cmd, *args, **kwargs):
        self._delegate.log(EXEC, cmd, *args, **kwargs)

    def set_level(self, level: int):
        self._delegate.setLevel(level)

    def add_handler(self, handler: logging.Handler):
        self._delegate.addHandler(handler)


def get_logger(name: Optional[str] = None) -> LoggerWrapper:
    return LoggerWrapper(delegate=logging.getLogger(name))


def bootstrap():
    logging.addLevelName(DEBUG, "DEBUG")
    logging.addLevelName(EXEC, "EXEC")
    logging.addLevelName(INFO, "INFO")
    logging.addLevelName(WARN, "WARN")
    logging.addLevelName(ERROR, "ERROR")
