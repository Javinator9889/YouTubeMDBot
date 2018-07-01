class Colors:
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    WARNING = "warning"
    FAIL = "fail"
    BOLD = "bold"
    UNDERLINE = "underline"
    RESET_ALL = "reset_all"


class OutputColors:
    colors = {Colors.RED: '\033[95m',
              Colors.BLUE: '\033[94m',
              Colors.GREEN: '\033[92m',
              Colors.WARNING: '\033[93m',
              Colors.FAIL: '\033[91m',
              Colors.BOLD: '\033[1m',
              Colors.UNDERLINE: '\033[4m',
              Colors.RESET_ALL: '\033[0m'}


def cPrint(text: str, color: Colors = None):
    colors = OutputColors.colors
    if color is None:
        color = colors[Colors.RESET_ALL]
    print(colors[color] + text + colors[Colors.RESET_ALL])
