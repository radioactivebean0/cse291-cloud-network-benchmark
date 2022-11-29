import typer
from kubernetes import config
from rich.pretty import pprint

from benchmarks import IPerfBenchmark
from util.terminal_ui import terminal_menu

app = typer.Typer(help="Benchmark runner for network benchmarks.")

config.load_kube_config()


@app.command()
def kubernetes(help="List all nodes in kubernetes cluster"):
    from kubernetes import client
    k8s_api = client.CoreV1Api()
    # nodes = [(node, 1) for node in k8s_api.list_node().items]
    nodes = k8s_api.list_node().items
    node_names = [node.metadata.name for node in nodes]

    client_node = terminal_menu("Choose a client to run on:", node_names)
    node_names = list(filter(lambda x: x != client_node, node_names))
    server_node = terminal_menu("Choose a server to run on:", node_names)
    nodes = None
    node_names = None

    input("Press enter to continue")
    benchmark_in_json = IPerfBenchmark(client_node=client_node, server_node=server_node).run()
    pprint(benchmark_in_json)


if __name__ == "__main__":
    app()
