import functools
from enum import StrEnum


class Color(StrEnum):
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"
    MAGENTA = "magenta"
    CYAN = "cyan"


# TODO: Fix colorize after bittensor update
def colorize(color: Color, text: str):
    return f"{text}"


red = functools.partial(colorize, Color.RED)
green = functools.partial(colorize, Color.GREEN)
yellow = functools.partial(colorize, Color.YELLOW)
blue = functools.partial(colorize, Color.BLUE)
magenta = functools.partial(colorize, Color.MAGENTA)
cyan = functools.partial(colorize, Color.CYAN)
