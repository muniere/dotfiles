from typing import TypeVar, Optional, Callable, Union

T = TypeVar('T')  # pylint: disable=invalid-name


def coalesce(value: Optional[T], default: Union[T, Callable[[], T]]) -> T:
    if value:
        return value

    if isinstance(default, Callable):
        return default()

    return default
