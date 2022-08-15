import os
from pathlib import Path
from typing import Union


def bin_(*other: Union[str, Path]) -> Path:
    return __factory('XDG_BIN_HOME', '~/.local/bin', *other)


def cache(*other: Union[str, Path]) -> Path:
    return __factory('XDG_CACHE_HOME', '~/.cache', *other)


def config(*other: Union[str, Path]) -> Path:
    return __factory('XDG_CONFIG_HOME', '~/.config', *other)


def data(*other: Union[str, Path]) -> Path:
    return __factory('XDG_DATA_HOME', '~/.local/share', *other)


def state(*other: Union[str, Path]) -> Path:
    return __factory('XDG_STATE_HOME', '~/.local/state', *other)


def runtime(*other: Union[str, Path]) -> Path:
    return __factory('XDG_RUNTIME_HOME', '~/.local/run', *other)


def __factory(key: str, default: str, *other: Union[str, Path]):
    return Path(os.getenv(key, default)).expanduser().joinpath(*other)
