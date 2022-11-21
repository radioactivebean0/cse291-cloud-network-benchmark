import subprocess
from datetime import datetime

from kubernetes import client as k8client, config

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

#from client.lib.kubernetes_integration import cli_chooser

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
        write_result(proc.stdout.read().decode("utf-8"))
        progress.update(proc_iperf, completed=1)

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
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    proc.wait()


if __name__ == "__main__":
    app()
