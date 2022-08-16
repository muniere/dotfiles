from typing import TypeVar, Optional, Generic

T = TypeVar('T')  # pylint: disable=invalid-name


class OptionalBox(Generic[T]):
    value: Optional[T]

    def __init__(self, value: Optional[T]):
        self.value = value

    def fold(self, default: T) -> T:
        if self.value:
            return self.value
        else:
            return default
