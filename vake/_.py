from typing import Callable, TypeVar, Optional

T = TypeVar('T')  # pylint: disable=invalid-name


class Box:
    value: any

    def __init__(self, value: any):
        self.value = value

    def fold(self, some: Callable[[], T], none: Callable[[], T]) -> T:
        if self.value:
            return some()
        else:
            return none()


def box(value: any) -> Box:
    return Box(value)


def safe(value: Optional[T], default: T) -> T:
    if value:
        return value
    else:
        return default
