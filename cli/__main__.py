import os

import typer
import yaml
from click import prompt
from kubernetes.utils import FailToCreateError
from rich.pretty import pprint

from util.kubernetes_integration import terminal_menu

app = typer.Typer(help="Benchmark runner for network benchmarks.")
from kubernetes import client, config, utils

config.load_kube_config()

def load_yaml_to_dicts(yaml_file):
    try:
        return _load_yaml_to_dicts(yaml_file)
    except FileNotFoundError as e:
        typer.echo("error: " + str(e))
        typer.echo(f"Could not find {yaml_file}")

        typer.Exit()

def _load_yaml_to_dicts(yaml_file):
    configs = []
    with open(os.path.abspath(yaml_file)) as f:
        yaml_file = yaml.safe_load_all(f)
        for doc in yaml_file:
            configs.append(doc)


    return configs



def iperf3_benchmark_kubernetes(client_node, server_node):

    typer.echo("Running iperf3 benchmark on Kubernetes")
    typer.echo(f"Deploying iperf3 server to {server_node}")
    k8api_client = client.ApiClient()

    client = dynamic.DynamicClient(
        api_client.ApiClient(configuration=config.load_kube_config())
    )
    api = client.resources.get(api_version="v1", kind="Node")


    configs = load_yaml_to_dicts("bandwidth/iperf3-server.yaml")
    deployment, service = configs

    nodeSelector = {"kubernetes.io/hostname": server_node}
    deployment["spec"]["template"]["spec"]["nodeSelector"] = nodeSelector

    utils.create_from_dict(k8api_client, deployment)
    utils.create_from_dict(k8api_client, service)
    input("server is running")
    utils.delete_from_dict(k8api_client, deployment)
    utils.delete_from_dict(k8api_client, service)





    input("Press enter to continue")



    typer.echo(f"Deployed iperf3 server to {server_node}")


@app.command()
def kubernetes(help="List all nodes in kubernetes cluster"):
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
    iperf3_benchmark_kubernetes(client_node, server_node)


if __name__ == "__main__":
    app()
