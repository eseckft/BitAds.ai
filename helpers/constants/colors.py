from enum import StrEnum


class Color(StrEnum):
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"
    MAGENTA = "magenta"
    CYAN = "cyan"
    WHITE = "white"


def colorize(color: Color, text: str):
    return f"<{color.value}>{text}</{color.value}>"
