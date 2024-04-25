import functools
from enum import Enum

from colorama import Style
from colorama.ansi import Fore


class Color(Enum):
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN


def colorize(color: Color, text: str):
    return f"{color.value}{text}{Style.RESET_ALL}"


red = functools.partial(colorize, Color.RED)
green = functools.partial(colorize, Color.GREEN)
yellow = functools.partial(colorize, Color.YELLOW)
blue = functools.partial(colorize, Color.BLUE)
magenta = functools.partial(colorize, Color.MAGENTA)
cyan = functools.partial(colorize, Color.CYAN)
