from enum import Enum


class AnsiColor(Enum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    RESET = 39

    def surround(self, obj: object) -> str:
        return f'{self.escape()}{obj}{AnsiColor.RESET.escape()}'

    def escape(self):
        return f'\033[{self.value}m'
