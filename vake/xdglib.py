import os
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Union

from . import kernel
from .kernel import Identity

__all__ = [
    'XdgContext',
    'bin_',
    'cache',
    'config',
    'data',
    'state',
    'runtime',
]


def bin_(*other: Union[str, Path]) -> Path:
    return XdgContext.auto().bin_(*other)


def cache(*other: Union[str, Path]) -> Path:
    return XdgContext.auto().cache(*other)


def config(*other: Union[str, Path]) -> Path:
    return XdgContext.auto().config(*other)


def data(*other: Union[str, Path]) -> Path:
    return XdgContext.auto().data(*other)


def state(*other: Union[str, Path]) -> Path:
    return XdgContext.auto().state(*other)


def runtime(*other: Union[str, Path]) -> Path:
    return XdgContext.auto().runtime(*other)


class XdgDefaults(metaclass=ABCMeta):

    @abstractmethod
    def bin_(self) -> Path:
        pass

    @abstractmethod
    def cache(self) -> Path:
        pass

    @abstractmethod
    def config(self) -> Path:
        pass

    @abstractmethod
    def data(self) -> Path:
        pass

    @abstractmethod
    def state(self) -> Path:
        pass

    @abstractmethod
    def runtime(self) -> Path:
        pass


class LinuxXdgDefaults(XdgDefaults):

    def bin_(self) -> Path:
        return Path('~/.local/bin').expanduser()

    def cache(self) -> Path:
        return Path('~/.cache').expanduser()

    def config(self) -> Path:
        return Path('~/.config').expanduser()

    def data(self) -> Path:
        return Path('~/.local/share').expanduser()

    def state(self) -> Path:
        return Path('~/.local/state').expanduser()

    def runtime(self) -> Path:
        return Path('~/.local/run').expanduser()


class DarwinXdgDefaults(XdgDefaults):

    def bin_(self) -> Path:
        return Path('~/.local/bin').expanduser()

    def cache(self) -> Path:
        return Path('~/.cache').expanduser()

    def config(self) -> Path:
        return Path('~/.config').expanduser()

    def data(self) -> Path:
        return Path('~/.local/share').expanduser()

    def state(self) -> Path:
        return Path('~/.local/state').expanduser()

    def runtime(self) -> Path:
        return Path('~/.local/run').expanduser()


class XdgContext:

    @classmethod
    def auto(cls) -> 'XdgContext':
        return cls.get(identity=kernel.identify())

    @classmethod
    def get(cls, identity: Identity) -> 'XdgContext':
        if identity.is_linux():
            return XdgContext(defaults=LinuxXdgDefaults())

        if identity.is_darwin():
            return XdgContext(defaults=DarwinXdgDefaults())

        raise ValueError('Windows not supported yet')

    def __init__(self, defaults: XdgDefaults):
        self.__defaults = defaults

    def bin_(self, *other: Union[str, Path]) -> Path:
        return self.__compose('XDG_BIN_HOME', str(self.__defaults.bin_()), *other)

    def cache(self, *other: Union[str, Path]) -> Path:
        return self.__compose('XDG_CACHE_HOME', str(self.__defaults.cache()), *other)

    def config(self, *other: Union[str, Path]) -> Path:
        return self.__compose('XDG_CONFIG_HOME', str(self.__defaults.config()), *other)

    def data(self, *other: Union[str, Path]) -> Path:
        return self.__compose('XDG_DATA_HOME', str(self.__defaults.data()), *other)

    def state(self, *other: Union[str, Path]) -> Path:
        return self.__compose('XDG_STATE_HOME', str(self.__defaults.state()), *other)

    def runtime(self, *other: Union[str, Path]) -> Path:
        return self.__compose('XDG_RUNTIME_HOME', str(self.__defaults.runtime()), *other)

    @staticmethod
    def __compose(key: str, default: str, *other: Union[str, Path]):
        return Path(os.getenv(key, default)).joinpath(*other)
