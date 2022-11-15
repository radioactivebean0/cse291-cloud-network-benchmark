import subprocess
import time
from datetime import datetime

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(help="Benchmark runner for network benchmarks.")


# destination is string of IP
# bandwidth is in Mbps for now, int values, default = 1Mbps
def iperf_continuous(destination, time = 10, bandwidth = 1):
    cmd = f"iperf3 -J -c {destination} -b {bandwidth}M -t {time}"
    return cmd

# perform iperf with some amount of time with unlimited bandwidth
def iperf_limitless(destination, time = 10):
    cmd = f"iperf3 -J -c {destination} -b 0 -t {time}"
    return cmd

def write_result(json: str):
    file_name = f"{datetime.now().isoformat()}.json"
    with open("results/" + file_name, "w") as f:
        f.write(json)

def bandwidth_test(destination):
    command = iperf_limitless(destination)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress:
        proc_iperf = progress.add_task(description="Running iperf test")
        proc.wait()
        progress.add_task(description="Writing result to file")
        write_result(proc.stdout.read().decode("utf-8"))
        progress.update(proc_iperf, completed=1)


@app.command()
def client(destination: str, perf_arguments: str = ""):
    bandwidth_test(destination)
    typer.echo("Test done")


def server():
    command = "iperf3 -s"
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    proc.wait()


if __name__ == "__main__":
    app()
