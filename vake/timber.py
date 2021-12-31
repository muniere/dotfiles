import logging
from enum import Enum
from typing import Optional

__all__ = [
    'Level', 'ColoredFormatter', 'StreamHandler', 'Lumber',
    'bootstrap', 'get_logger',
]


class Level(Enum):
    DEBUG = 10
    EXEC = 15
    INFO = 20
    WARN = 30
    ERROR = 40


class ColoredFormatter(logging.Formatter):
    LEVEL_NAME_WIDTH = 5

    def format(self, record: logging.LogRecord):
        label = record.levelname.ljust(self.__class__.LEVEL_NAME_WIDTH)
        message = record.getMessage()
        levelno = record.levelno
        return self.colorize(f"[{label}] {message}", levelno=levelno)

    @staticmethod
    def colorize(message, levelno=logging.NOTSET):
        reset_str = "\033[0m"

        color_dict = {
            Level.DEBUG.value: "\033[32m",  # green
            Level.EXEC.value: "\033[35m",  # magenta
            Level.INFO.value: "\033[36m",  # cyan
            Level.WARN.value: "\033[33m",  # yellow
            Level.ERROR.value: "\033[33m",  # red
        }

        color_str = color_dict.get(levelno, reset_str)

        return f"{color_str}{message}{reset_str}"


class StreamHandler(logging.StreamHandler):

    def set_level(self, level: Level):
        self.setLevel(level.value)

    def set_formatter(self, formatter: ColoredFormatter):
        self.setFormatter(formatter)


class Lumber:

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
        self._delegate.log(Level.EXEC.value, cmd, *args, **kwargs)

    def set_level(self, level: Level):
        self._delegate.setLevel(level.value)

    def add_handler(self, handler: logging.Handler):
        self._delegate.addHandler(handler)


def get_logger(name: Optional[str] = None) -> Lumber:
    return Lumber(delegate=logging.getLogger(name))


def bootstrap():
    logging.addLevelName(Level.DEBUG.value, "DEBUG")
    logging.addLevelName(Level.EXEC.value, "EXEC")
    logging.addLevelName(Level.INFO.value, "INFO")
    logging.addLevelName(Level.WARN.value, "WARN")
    logging.addLevelName(Level.ERROR.value, "ERROR")
