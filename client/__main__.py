import subprocess
import time
import os
from datetime import datetime
import json

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from metrics import calculate_retransmission, calculate_latency, calculate_jitter
from visual import draw_plot

app = typer.Typer(help="Benchmark runner for network benchmarks.")


def write_result(json: str):
    file_name = f"{datetime.now().isoformat()}.json"
    with open("results/" + file_name, "w") as f:
        f.write(json)


@app.command()
def client(destination: str, perf_arguments: str = ""):
    command = f"iperf3 -J -c {destination} {perf_arguments}"
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress:
        proc_iperf = progress.add_task(description="Running iperf test")
        proc.wait()
        progress.add_task(description="Writing result to file")
        content = proc.stdout.read().decode("utf-8")
        write_result(content)

        typer.echo("Calculating performance metrics")
        json_dict = json.loads(content)
        retrans = calculate_retransmission(json_dict)
        latency = calculate_latency(json_dict)
        jitter = calculate_jitter(json_dict)

        typer.echo("Generating plots for visualization")
        draw_plot(retrans, "retransmission", "images/retransmission.png")
        draw_plot(latency, "latency", "images/latency.png")
        draw_plot(jitter, "jitter", "images/jitter.png")

        proc = subprocess.Popen("ls results", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        result = proc.stdout.read().decode("utf-8")
        typer.echo(result)

        progress.update(proc_iperf, completed=1)

    typer.echo("Test done")


def server():
    command = "iperf3 -s"
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    proc.wait()


if __name__ == "__main__":
    app()
