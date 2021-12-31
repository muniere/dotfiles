import logging
from abc import ABCMeta, abstractmethod
from enum import Enum

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


class Lumber(metaclass=ABCMeta):

    @staticmethod
    def noop() -> 'Lumber':
        return NoopLumber()

    @abstractmethod
    def debug(self, msg, *args, **kwargs):
        pass

    @abstractmethod
    def info(self, msg, *args, **kwargs):
        pass

    @abstractmethod
    def warn(self, msg, *args, **kwargs):
        pass

    @abstractmethod
    def warning(self, msg, *args, **kwargs):
        pass

    @abstractmethod
    def error(self, msg, *args, **kwargs):
        pass

    @abstractmethod
    def execute(self, cmd, *args, **kwargs):
        pass

    @abstractmethod
    def set_level(self, level: Level):
        pass

    @abstractmethod
    def add_handler(self, handler: logging.Handler):
        pass


class DefaultLumber(Lumber):

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


class NoopLumber(Lumber):

    def debug(self, msg, *args, **kwargs):
        pass

    def info(self, msg, *args, **kwargs):
        pass

    def warn(self, msg, *args, **kwargs):
        pass

    def warning(self, msg, *args, **kwargs):
        pass

    def error(self, msg, *args, **kwargs):
        pass

    def execute(self, cmd, *args, **kwargs):
        pass

    def set_level(self, level: Level):
        raise RuntimeError("Cannot set level for noop")

    def add_handler(self, handler: logging.Handler):
        raise RuntimeError("Cannot add handler for noop")


def get_logger(name: str) -> Lumber:
    return DefaultLumber(delegate=logging.getLogger(name))


def bootstrap():
    logging.addLevelName(Level.DEBUG.value, "DEBUG")
    logging.addLevelName(Level.EXEC.value, "EXEC")
    logging.addLevelName(Level.INFO.value, "INFO")
    logging.addLevelName(Level.WARN.value, "WARN")
    logging.addLevelName(Level.ERROR.value, "ERROR")
