import logging

import typer
from kubernetes import config
from rich.pretty import pprint

from k8perf.benchmarks import IPerfBenchmark
from k8perf.util_terminal_ui import terminal_menu, show_result
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(help="Benchmark runner for network benchmarks.")

config.load_kube_config()


@app.command()
def kubernetes(delete_pods: bool = True, debug: bool = False, json: bool = False):
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    from kubernetes import client

    k8s_api = client.CoreV1Api()
    # nodes = [(node, 1) for node in k8s_api.list_node().items]
    nodes = k8s_api.list_node().items
    node_names = [node.metadata.name for node in nodes]
    nodes = None

    server_node = terminal_menu("Choose a server to run on:", node_names)
    client_node = terminal_menu("Choose a client to run on:", node_names)
    node_names = None
    if client_node is None or server_node is None:
        typer.echo("Exiting...")
        raise typer.Exit()

    if server_node == client_node:
        typer.echo("FIY: Server and client are the same node.")
    confirm = input("Do you wanna deploy on these nodes? [y/n] ")
    if confirm.lower() != "y":
        raise typer.Exit()

    # loading animation
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task1 = progress.add_task(description="Running benchmark", total=None)
        benchmark = IPerfBenchmark(client_node=client_node, server_node=server_node)
        benchmark_in_json = benchmark.run()
        progress.update(task1, description="Cleaning up")
        if delete_pods:
            benchmark.cleanup()

    if json:
        pprint(benchmark_in_json)
    else:
        show_result(benchmark_in_json)
    typer.echo("Done!")


if __name__ == "__main__":
    app()
