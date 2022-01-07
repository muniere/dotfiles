import logging
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .tty import Color

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
    values: dict[int, Color]

    @staticmethod
    def default() -> 'ColorPalette':
        return ColorPalette({
            Level.DEBUG.value: Color.GREEN,
            Level.EXEC.value: Color.MAGENTA,
            Level.INFO.value: Color.CYAN,
            Level.WARN.value: Color.YELLOW,
            Level.ERROR.value: Color.RESET,
        })

    def get(self, key: int) -> Color:
        return self.values.get(key, Color.RESET)


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
        return color.decorate(message)


class StreamHandler(logging.StreamHandler):

    def emit(self, record: logging.LogRecord) -> None:
        # noinspection PyBroadException
        # pylint: disable=broad-except
        try:
            msg = self.format(record)
            stream = self.stream
            if record.__dict__.get('terminate', True):
                stream.write(msg + self.terminator)
            else:
                stream.write(msg)
            self.flush()
        except RecursionError:  # See issue 36272
            raise
        except Exception:
            self.handleError(record)
        # pylint: enable=broad-except

    def set_level(self, level: Level):
        self.setLevel(level.value)

    def set_formatter(self, formatter: TaggedFormatter):
        self.setFormatter(formatter)


class Lumber(metaclass=ABCMeta):

    @staticmethod
    def noop() -> 'Lumber':
        return NoopLumber()

    @abstractmethod
    def debug(self, msg: object, terminate: bool = False):
        pass

    @abstractmethod
    def info(self, msg: object, terminate: bool = False):
        pass

    @abstractmethod
    def warn(self, msg: object, terminate: bool = False):
        pass

    @abstractmethod
    def warning(self, msg: object, terminate: bool = False):
        pass

    @abstractmethod
    def error(self, msg: object, terminate: bool = False):
        pass

    @abstractmethod
    def execute(self, msg: object, terminate: bool = False):
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

    def debug(self, msg: object, terminate: bool = True):
        self._delegate.debug(msg, extra={'terminate': terminate})

    def info(self, msg: object, terminate: bool = True):
        self._delegate.info(msg, extra={'terminate': terminate})

    def warn(self, msg: object, terminate: bool = True):
        self._delegate.warning(msg, extra={'terminate': terminate})

    def warning(self, msg: object, terminate: bool = True):
        self._delegate.warning(msg, extra={'terminate': terminate})

    def error(self, msg: object, terminate: bool = True):
        self._delegate.error(msg, extra={'terminate': terminate})

    def execute(self, msg, terminate: bool = True):
        self._delegate.log(Level.EXEC.value, msg, extra={'terminate': terminate})

    def set_level(self, level: Level):
        self._delegate.setLevel(level.value)

    def add_handler(self, handler: logging.Handler):
        self._delegate.addHandler(handler)


class NoopLumber(Lumber):

    def debug(self, msg: object, terminate: bool = True):
        pass

    def info(self, msg: object, terminate: bool = True):
        pass

    def warn(self, msg: object, terminate: bool = True):
        pass

    def warning(self, msg: object, terminate: bool = True):
        pass

    def error(self, msg: object, terminate: bool = True):
        pass

    def execute(self, msg: object, terminate: bool = True):
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
