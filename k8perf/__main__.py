import rich
import typer
from kubernetes import config

from k8perf.benchmarks import IPerfBenchmark
from k8perf.util_terminal_ui import terminal_menu
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(help="Benchmark runner for network benchmarks.")

config.load_kube_config()


def show_result(benchmark_in_json):
    throughput = benchmark_in_json["end"]["sum_received"]["bits_per_second"] / 1000000
    cpu_host = benchmark_in_json["end"]["cpu_utilization_percent"]["host_total"]
    cpu_client = benchmark_in_json["end"]["cpu_utilization_percent"]["remote_total"]

    rich.print(f"[bold green]Throughput: {format(throughput, '.2f')} Mbps/s [/bold green][bold blue]CPU host: {format(cpu_host, '.2f')}%[/bold blue][bold cyan] CPU client: {format(cpu_client, '.2f')}% [/bold cyan]")



@app.command()
def kubernetes(help="List all nodes in kubernetes cluster", debug: bool = False):
    from kubernetes import client
    k8s_api = client.CoreV1Api()
    # nodes = [(node, 1) for node in k8s_api.list_node().items]
    nodes = k8s_api.list_node().items
    node_names = [node.metadata.name for node in nodes]
    nodes = None

    server_node = terminal_menu("Choose a server to run on:", node_names)
    node_names = list(filter(lambda x: x != server_node, node_names))
    client_node = terminal_menu("Choose a client to run on:", node_names)
    node_names = None
    if client_node is None or server_node is None:
        typer.echo("Exiting...")
        raise typer.Exit()

    confirm = input("Do you wanna deploy on these nodes? [y/n] ")
    if confirm != "y":
        raise typer.Exit()

    # loading animation
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress:
        progress.add_task(description="Running benchmark", total=None)
        benchmark_in_json = IPerfBenchmark(client_node=client_node, server_node=server_node).run()
    show_result(benchmark_in_json)
    typer.echo("Done!")


if __name__ == "__main__":
    app()
