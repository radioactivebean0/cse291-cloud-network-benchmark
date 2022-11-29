from typing import Any, Optional, IO

import typer
from InquirerPy import inquirer
from InquirerPy.base import Choice
from InquirerPy.separator import Separator
from rich import print

DEBUG = True


def debug_log(
        *objects: Any,
        sep: str = " ",
        end: str = "\n",
        file: Optional[IO[str]] = None,
        flush: bool = False,
) -> None:
    if DEBUG:
        print(*objects, sep=sep, end=end, file=file, flush=flush)


def terminal_menu(message, nodes):
    choices = nodes + [Separator(), Choice(value=None, name="Exit")]
    action = inquirer.select(
        message=message,
        choices=choices
    ).execute()

    if action is None:
        typer.Exit()

    return action


