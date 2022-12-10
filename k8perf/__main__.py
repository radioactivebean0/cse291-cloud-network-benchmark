import json
import logging
from typing import Dict
import matplotlib.pyplot as plt
import numpy as np

import pandas as pandas
import typer
from kubernetes import config
from kubernetes.client import V1NodeList, V1Node
from rich.pretty import pprint

from k8perf.benchmark import BenchmarkRunner
from k8perf.benchmarks import IPerfBenchmark
from k8perf.util_terminal_ui import terminal_menu, show_result, bytes_to_human_readable
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(help="Benchmark runner for network benchmarks.")

config.load_kube_config()


def parse_benchmark_json(benchmark_json: Dict) -> (float, float, float):
    """Parse benchmark json to get mbps and cpu usage."""
    bps = benchmark_json["end"]["sum_received"]["bits_per_second"]
    cpu_host = float(benchmark_json["end"]["cpu_utilization_percent"]["host_total"])
    cpu_client = float(benchmark_json["end"]["cpu_utilization_percent"]["host_total"])
    mean_rtt = float(benchmark_json["end"]["streams"][0]["sender"]["mean_rtt"])
    retransmits = int(benchmark_json["end"]["streams"][0]["sender"]["retransmits"])

    return bps, cpu_host, cpu_client, mean_rtt, retransmits


def benchmark_all_nodes(nodes: V1NodeList.items):
    """Benchmark all nodes in the cluster."""
    benchmark_pd = pandas.DataFrame()
    json_results = []
    node_names = [node.metadata.name for node in nodes]
    for client_node in node_names:
        for server_node in node_names:
            benchmark = IPerfBenchmark(client_node=client_node, server_node=server_node)
            benchmark_json = benchmark.run()
            json_results.append(benchmark_json)
            mbps, cpu_host, cpu_client, mean_rtt, retransmits = parse_benchmark_json(benchmark_json)
            benchmark_pd = benchmark_pd.append(
                {
                    "client_node": client_node,
                    "server_node": server_node,
                    "mbps": mbps,
                    "cpu_host": cpu_host,
                    "cpu_client": cpu_client,
                    "mean_rtt": mean_rtt,
                    "retransmits": retransmits
                },
                ignore_index=True,
            )
    print(benchmark_pd)
    benchmark_pd.to_csv("benchmark.csv")
    with open("benchmark.json", "w") as f:
        f.write(str(json_results))


@app.command()
def kubernetes(delete_pods: bool = True, debug: bool = False, json: bool = False, all_nodes: bool = False,
               plot: bool = False, csv: str = None):
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    from kubernetes import client

    k8s_api = client.CoreV1Api()
    # nodes = [(node, 1) for node in k8s_api.list_node().items]
    # get nodes that do not have "noSchedule" taint
    nodes = [node for node in k8s_api.list_node().items if not node.spec.taints]

    if all_nodes:
        benchmark_all_nodes(nodes)
        raise typer.Exit()

    node_names = [node.metadata.name for node in nodes]
    nodes = None

    server_nodes = terminal_menu("Choose a server to run on:", node_names)
    client_nodes = terminal_menu("Choose a client to run on:", node_names)
    node_names = None
    if "None" in client_nodes or "None" in server_nodes:
        typer.echo("Exiting...")
        raise typer.Exit()

    if any(node in server_nodes for node in client_nodes):
        typer.echo("FIY: You have a benchmark running both as a client and server on the same node")
    confirm = input("Do you wanna deploy on these nodes? [y/n] ")
    if confirm.lower() != "y":
        raise typer.Exit()

    # loading animation
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress:
        runner = BenchmarkRunner(client_node_names=client_nodes, server_node_names=server_nodes)
        runner.run()
        if delete_pods:
            runner.cleanup()

    if json:
        pprint(runner.json())
    else:
        pprint(runner.benchmark_results)

    if csv is not None:
        runner.benchmark_results.results.to_csv(csv)

    if plot:
        typer.echo("plot")

    typer.echo("Done!")


@app.command()
def plot_latency():
    df = pandas.read_csv("benchmark.csv")

    df = df.pivot(index="client_node", columns="server_node", values="mbps")

    plot_from_df(df, {
        "aks-agentpool-45773067-vmss000000": "US East AZ-1 D4v2",
        "aks-multizone-35578676-vmss000000": "US East AZ-2 B2",
        "aks-multizone-35578676-vmss000001": "US East AZ-2 B2"}
                 , "Blues",
                 lambda val: "white" if val > 1e10 else "black",
                 lambda val: bytes_to_human_readable(val),
                 "Mbps between availability zones d3")


@app.command()
def plot_rtt():
    df = pandas.read_csv("benchmark.csv")

    df = df.pivot(index="client_node", columns="server_node", values="mean_rtt")
    plot_from_df(df, {
        "aks-agentpool-45773067-vmss000000": "US East AZ-1 D4v2",
        "aks-multizone-35578676-vmss000000": "US East AZ-2 B2",
        "aks-multizone-35578676-vmss000001": "US East AZ-2 B2"}
                 , "hot",
                 lambda value: "white" if value < 7000 else "black",
                 lambda val: str(val) + "ms",
                 "RTT on d3 (most popular azure)")


@app.command()
def plot_rets():
    df = pandas.read_csv("benchmark.csv")

    df = df.pivot(index="client_node", columns="server_node", values="retransmits")
    plot_from_df(df, {
        "aks-agentpool-45773067-vmss000000": "US East AZ-1 D4v2",
        "aks-multizone-35578676-vmss000000": "US East AZ-2 B2",
        "aks-multizone-35578676-vmss000001": "US East AZ-2 B2"}
                 , "Greens",
                 lambda value: "white" if value > 4000 else "black",
                 lambda val: str(val),
                 "retransmissions")


# colorpicker: (value: Any) -> str
def plot_from_df(df, type_mapping: Dict, colormap: str, color_picker, annotation, title: str):
    print(df)
    server_names = [type_mapping[node] for node in df.columns.tolist()]
    client_names = [type_mapping[node] for node in df.index.tolist()]
    from matplotlib.figure import Figure
    from matplotlib.axes import Axes
    fig: Figure
    ax: Axes
    fig, ax = plt.subplots()
    im = ax.imshow(df, cmap=colormap)
    # Show all ticks and label them with the respective list entries
    ax.set_xticks(np.arange(len(server_names)), labels=server_names)
    ax.set_yticks(np.arange(len(client_names)), labels=client_names)
    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")
    # fix tickrate to human readable
    fig.colorbar(im)
    ax.set_xlabel("server")
    ax.set_ylabel("client")
    for i in range(len(client_names)):
        for j in range(len(server_names)):
            color = color_picker(df.iloc[i, j])
            text = ax.text(j, i, annotation(df.iloc[i, j]),
                           ha="center", va="center", color=color)
    ax.set_title(title)
    fig.tight_layout()
    plt.show()


@app.command()
def parse_json():
    json_b = ""
    with open("benchmark.json") as f:
        json_b = f.read()

    benchmark_pd = pandas.DataFrame()
    benchmarks = json.loads(json_b)
    benchmarks.reverse()
    node_names = ["aks-agentpool-45773067-vmss000000", "aks-multizone-35578676-vmss000000",
                  "aks-multizone-35578676-vmss000001"]
    for client_node in node_names:
        for server_node in node_names:
            mbps, cpu_host, cpu_client, mean_rtt, retransmits = parse_benchmark_json(benchmarks.pop())
            benchmark_pd = benchmark_pd.append(
                {
                    "client_node": client_node,
                    "server_node": server_node,
                    "mbps": mbps,
                    "cpu_host": cpu_host,
                    "cpu_client": cpu_client,
                    "mean_rtt": mean_rtt,
                    "retransmits": retransmits

                },
                ignore_index=True,
            )

    print(benchmark_pd)
    benchmark_pd.to_csv("benchmark.csv")


@app.command()
def mbps(_mbps: float):
    typer.echo(bytes_to_human_readable(_mbps * 1e6))


@app.command()
def money():
    df = pandas.read_csv("/Users/andersspringborg/Downloads/Splitwise expenses Nov 30.csv")
    costs_where_steffi_is_minus = df["Cost"].where(df["Steffi"] < 0).dropna()
    # parse cost column into int
    list_of_people = ["Steffi", "Fine", "Anders Aaen Springborg", "Nicolai", "Nani Kang", "Paul Volk", "Michelle",
                      "Patrick"]
    df = df.assign(Cost=df["Cost"].str.replace(" ", "0").astype(float))
    people_in_plus = [(person, (df["Cost"].where(df[person] > 0).dropna()).sum()) for person in list_of_people]

    pprint(people_in_plus)
    # print(costs_where_steffi_is_minus.sum())


if __name__ == "__main__":
    app()

# https://www.cockroachlabs.com/blog/cockroachdb-kubernetes-cilium/
