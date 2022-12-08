import logging
from typing import Dict, List

import pandas

from k8perf.benchmarks import IPerfBenchmark


class BenchmarkResult:
    client_node: str
    server_node: str
    mbps: float
    cpu_host: float
    cpu_client: float
    mean_rtt: float
    retransmits: int

    def __init__(self, client_node: str, server_node: str):
        self.client_node = client_node
        self.server_node = server_node

    def __repr__(self):
        return f"Mbps: {self.mbps}, cpu_host: {self.cpu_host}, cpu_client: {self.cpu_client}, mean_rtt: {self.mean_rtt}, retransmits: {self.retransmits}"

    def add_iperf3(self, iperf3_json: Dict):
        self.mbps = iperf3_json["end"]["sum_received"]["bits_per_second"] * 1e6
        self.cpu_host = float(iperf3_json["end"]["cpu_utilization_percent"]["host_total"])
        self.cpu_client = float(iperf3_json["end"]["cpu_utilization_percent"]["host_total"])
        self.mean_rtt = float(iperf3_json["end"]["streams"][0]["sender"]["mean_rtt"])
        self.retransmits = int(iperf3_json["end"]["streams"][0]["sender"]["retransmits"])


class BenchmarkResults:
    def __init__(self):
        self.results = pandas.DataFrame()

    def add_result(self, benchmark_run: BenchmarkResult):
        self.results = self.results.append(
            {
                "server_node": benchmark_run.server_node,
                "client_node": benchmark_run.client_node,
                "mbps": benchmark_run.mbps,
                "cpu_host": benchmark_run.cpu_host,
                "cpu_client": benchmark_run.cpu_client,
                "mean_rtt": benchmark_run.mean_rtt,
                "retransmits": benchmark_run.retransmits
            }, ignore_index=True)

    def __str__(self):
        return str(self.results)

    def __repr__(self):
        return str(self.results)

    def json(self):
        return self.results.to_json()


class BenchmarkRunner:
    def __init__(self, client_node_names: List[str], server_node_names: List[str]):
        self.client_nodes = client_node_names
        self.server_nodes = server_node_names
        self.benchmark_results: BenchmarkResults = BenchmarkResults()

    def run(self):
        for server_node in self.server_nodes:
            for client_node in self.client_nodes:
                logging.info("Running benchmark server %s: client: %s", client_node, server_node)
                benchmark = BenchmarkResult(client_node, server_node)
                iperfBenchmarkResult = IPerfBenchmark(client_node, server_node).run()
                benchmark.add_iperf3(iperfBenchmarkResult)

                self.benchmark_results.add_result(benchmark)

    def cleanup(self):
        IPerfBenchmark("", "").cleanup()

    def json(self):
        return self.benchmark_results.json()
