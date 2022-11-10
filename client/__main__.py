import subprocess
import time
from datetime import datetime

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(help="Benchmark runner for network benchmarks.")

# we may need to add more parameters to smoothen out transmission if we
# go to higher bitrates or even use multiprocessing.

# destination is string of IP
# bandwidth is in Mbps for now, int values, default = 1Mbps
# isUDP defines if UDP or TCP test, default is TCP test
# bidir is an arg to do tests in both directions, default is false
def iperfContinuous(destination, time = 10, bandwidth = 1, isUDP = False, bidir = False):
    cmd = f"iperf3 -J -c {destination} -b {bandwidth}M -t {time}"
    if isUDP:
        cmd = cmd + " -u"
    if bidir:
        cmd = cmd + " -d"
    return cmd
'''
def iperfBurst(destination, burst_size, isUDP = False, bidir = False):
    cmd = f"iperf3 -J -c {destination} -b 1280K/{burst_size} --pacing-timer 1000000"
    if isUDP:
        cmd = cmd + " -u"
    if bidir:
        cmd = cmd + " -d"
    return cmd
'''

def write_result(json: str):
    file_name = f"{datetime.now().isoformat()}.json"
    with open("results/" + file_name, "w") as f:
        f.write(json)


@app.command()
def client(destination: str, perf_arguments: str = ""):
    command = iperfBurst(destination, 2)
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

    typer.echo("Test done")


def server():
    command = "iperf3 -s"
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    proc.wait()


if __name__ == "__main__":
    app()
