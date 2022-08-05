from typing import Callable, TypeVar, Optional, Generic

T = TypeVar('T')  # pylint: disable=invalid-name


class BoolBox:
    value: bool

    def __init__(self, value: bool):
        self.value = value

    def fold(self, truthy: Callable[[], T], falsy: Callable[[], T]) -> T:
        if self.value:
            return truthy()
        else:
            return falsy()


class TernaryBox:
    value: any

    def __init__(self, value: any):
        self.value = value

    def fold(self, some: Callable[[], T], none: Callable[[], T]) -> T:
        if self.value:
            return some()
        else:
            return none()


class OptionalBox(Generic[T]):
    value: Optional[T]

    def __init__(self, value: Optional[T]):
        self.value = value

    def fold(self, default: T) -> T:
        if self.value:
            return self.value
        else:
            return default
