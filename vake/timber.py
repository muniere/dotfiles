import logging
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .ansi import AnsiColor

__all__ = [
    'Level', 'TaggedFormatter', 'StreamHandler', 'Lumber',
    'bootstrap', 'get_logger',
]


class Level(Enum):
    DEBUG = 10
    EXEC = 15
    INFO = 20
    WARN = 30
    ERROR = 40


@dataclass(frozen=True)
class ColorPalette:
    values: dict[int, AnsiColor]

    @staticmethod
    def default() -> 'ColorPalette':
        return ColorPalette({
            Level.DEBUG.value: AnsiColor.GREEN,
            Level.EXEC.value: AnsiColor.MAGENTA,
            Level.INFO.value: AnsiColor.CYAN,
            Level.WARN.value: AnsiColor.YELLOW,
            Level.ERROR.value: AnsiColor.RESET,
        })

    def get(self, key: int) -> AnsiColor:
        return self.values.get(key, AnsiColor.RESET)


class TaggedFormatter(logging.Formatter):
    __palette: ColorPalette
    __label: int

    @classmethod
    def default(cls, label: int = 5):
        return cls(palette=None, label=label)

    @classmethod
    def colored(cls, label: int = 5):
        return cls(palette=ColorPalette.default(), label=label)

    def __init__(self, palette: Optional[ColorPalette] = None, label: int = 5):
        super().__init__()
        self.__palette = palette
        self.__label = label
        return

    def format(self, record: logging.LogRecord):
        base = record.getMessage()
        label = record.levelname.ljust(self.__label)
        message = f'[{label}] {base}'

        if not self.__palette:
            return message

        color = self.__palette.get(record.levelno)
        return color.surround(message)


class StreamHandler(logging.StreamHandler):

    def set_level(self, level: Level):
        self.setLevel(level.value)

    def set_formatter(self, formatter: TaggedFormatter):
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
        raise RuntimeError('Cannot set level for noop')

    def add_handler(self, handler: logging.Handler):
        raise RuntimeError('Cannot add handler for noop')


def get_logger(name: str) -> Lumber:
    return DefaultLumber(delegate=logging.getLogger(name))


def bootstrap():
    logging.addLevelName(Level.DEBUG.value, 'DEBUG')
    logging.addLevelName(Level.EXEC.value, 'EXEC')
    logging.addLevelName(Level.INFO.value, 'INFO')
    logging.addLevelName(Level.WARN.value, 'WARN')
    logging.addLevelName(Level.ERROR.value, 'ERROR')
