from typing import TypeVar, Optional

T = TypeVar('T')  # pylint: disable=invalid-name


def safe(value: Optional[T], default: T) -> T:
    if value:
        return value
    else:
        return default
