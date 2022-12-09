from typing import Any, Optional, IO

import rich
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


def terminal_menu(message, nodes) -> [str]:
    choices = nodes + [Separator(), Choice(value="All", name="All nodes"), Choice(value="None", name="Exit")]
    action = inquirer.select(message=message, choices=choices).execute()

    if action is None:
        raise typer.Exit()

    if action == "All":
        return nodes

    return [action]


def bytes_to_human_readable(bytes):
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit = 0
    while bytes > 1024:
        bytes /= 1024
        unit += 1
    return f"{bytes:.0f} {units[unit]}/s"


def show_result(benchmark_in_json):
    throughput = benchmark_in_json["end"]["sum_received"]["bits_per_second"]
    cpu_host = benchmark_in_json["end"]["cpu_utilization_percent"]["host_total"]
    cpu_client = benchmark_in_json["end"]["cpu_utilization_percent"]["remote_total"]

    rich.print(
        f"[bold green]Throughput: {bytes_to_human_readable(throughput)} [/bold green][bold blue]CPU host: {format(cpu_host, '.2f')}%[/bold blue][bold cyan] CPU client: {format(cpu_client, '.2f')}% [/bold cyan]"
    )
