import logging
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
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


class AnsiColor(Enum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    RESET = 39

    def escape(self):
        return f'\033[{self.value}m'


@dataclass(frozen=True)
class AnsiColorPalette:
    values: dict[int, AnsiColor]

    @staticmethod
    def default() -> 'AnsiColorPalette':
        return AnsiColorPalette({
            Level.DEBUG.value: AnsiColor.GREEN,
            Level.EXEC.value: AnsiColor.MAGENTA,
            Level.INFO.value: AnsiColor.CYAN,
            Level.WARN.value: AnsiColor.YELLOW,
            Level.ERROR.value: AnsiColor.RESET,
        })

    def get(self, key: int) -> AnsiColor:
        return self.values.get(key, AnsiColor.RESET)


class ColoredFormatter(logging.Formatter):
    __palette: AnsiColorPalette
    __label: int

    def __init__(self, palette: AnsiColorPalette = AnsiColorPalette.default(), label: int = 5):
        super().__init__()
        self.__palette = palette
        self.__label = label
        return

    def format(self, record: logging.LogRecord):
        label = record.levelname.ljust(self.__label)
        message = record.getMessage()
        prefix = self.__palette.get(record.levelno).escape()
        suffix = AnsiColor.RESET.escape()
        return f'{prefix}[{label}] {message}{suffix}'


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
