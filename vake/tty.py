from enum import Enum
from typing import List


class Color(Enum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    RESET = 39

    def decorate(self, obj: object, bold: bool = False) -> str:
        base = f'{self.escape()}{obj}{Color.RESET.escape()}'
        if bold:
            return f'\033[1m{base}\033[0m'
        else:
            return base

    def escape(self):
        return f'\033[{self.value}m'


class Looper:
    __seq: List[str]
    __i: int

    @classmethod
    def spin(cls, clockwise: bool = True) -> 'Looper':
        seq = ['|', '/', '-', '\\']
        if clockwise:
            return Looper(seq)
        else:
            return Looper(list(reversed(seq)))

    @classmethod
    def dots(cls, clockwise: bool = True) -> 'Looper':
        seq = ['⣷', '⣯', '⣟', '⡿', '⢿', '⣻', '⣽', '⣾']
        if clockwise:
            return Looper(seq)
        else:
            return Looper(list(reversed(seq)))

    def __init__(self, seq: List[str]):
        self.__seq = seq
        self.__i = 0

    def __next__(self):
        char = self.__seq[self.__i]
        self.__i = (self.__i + 1) % len(self.__seq)
        return char

    def __iter__(self):
        return self
