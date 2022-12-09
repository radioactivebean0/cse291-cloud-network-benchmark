import subprocess
from datetime import datetime

from kubernetes import client as k8client, config

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

# from client.lib.kubernetes_integration import cli_chooser

app = typer.Typer(help="Benchmark runner for network benchmarks.")


# destination is string of IP
# bandwidth is in Mbps for now, int values, default = 1Mbps
def iperf_continuous(destination, time=10, bandwidth=1):
    cmd = f"iperf3 -J -c {destination} -b {bandwidth}M -t {time}"
    return cmd


# perform iperf with some amount of time with unlimited bandwidth
def iperf_limitless(destination, time=10):
    cmd = f"iperf3 -J -c {destination} -b 0 -t {time}"
    return cmd


def write_result(json: str, experiment_id):
    file_name = f"{datetime.now().isoformat()}-{experiment_id}.json"
    with open("results/" + file_name, "w") as f:
        f.write(json)


def bandwidth_test(destination):
    command = iperf_limitless(destination)
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        proc_iperf = progress.add_task(description="Running iperf bw test")
        proc.wait()
        progress.add_task(description="Writing result to file")
        write_result(proc.stdout.read().decode("utf-8"), "bw_test")
        progress.update(proc_iperf, completed=1)


def rtt_loss_test(destination, bandwidth):
    command = iperf_continuous(destination, bandwidth=bandwidth)
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        proc_iperf = progress.add_task(description="Running iperf rtt,loss test")
        proc.wait()
        progress.add_task(description="Writing result to file")
        write_result(proc.stdout.read().decode("utf-8"), "rtt_loss_test")
        progress.update(proc_iperf, completed=1)


@app.command()
def client(destination: str, perf_arguments: str = ""):
    bandwidth_test(destination)
    rtt_loss_test(destination, 1000)
    typer.echo("Test done")


@app.command()
def kubernetes():
    config.load_kube_config()

    api_instance = k8client.CoreV1Api()
    node_list = api_instance.list_node()

    client1, server1 = cli_chooser(node_list.items)
    # list all nodes

    # print chosen nodes
    typer.echo(f"Client: {client1}")
    typer.echo(f"Server: {server1}")


def server():
    command = "iperf3 -s"
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    )
    proc.wait()


if __name__ == "__main__":
    app()
