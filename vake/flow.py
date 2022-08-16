from typing import Callable, TypeVar

T = TypeVar('T')  # pylint: disable=invalid-name


def branch(value: any, truthy: Callable[[], T], falsy: Callable[[], T]) -> T:
    if value:
        return truthy()
    else:
        return falsy()
