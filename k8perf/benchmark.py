import logging
from typing import Dict, List

import pandas

from k8perf.benchmarks import IPerfBenchmark, LocustBenchmark


class BenchmarkResult:
    client_node: str = ""
    server_node: str = ""
    mbps: float = 0.0
    cpu_server: float = 0.0
    cpu_client: float = 0.0
    mean_rtt: float = 0.0
    retransmits: int = 0

    httpMinResponseTime: int
    httpMaxResponseTime: int
    httpMedianResponseTime: int
    httpAverageResponseTime: int

    def __init__(self, client_node: str, server_node: str):
        self.client_node = client_node
        self.server_node = server_node

    def __repr__(self):
        return f"Mbps: {self.mbps}, cpu_host: {self.cpu_server}, cpu_client: {self.cpu_client}, mean_rtt: {self.mean_rtt}, retransmits: {self.retransmits}"

    def add_iperf3(self, iperf3_json: Dict):
        self.mbps = iperf3_json["end"]["sum_received"]["bits_per_second"] / 1e6
        self.cpu_server = float(iperf3_json["end"]["cpu_utilization_percent"]["remote_total"])
        self.cpu_client = float(iperf3_json["end"]["cpu_utilization_percent"]["host_total"])
        self.mean_rtt = float(iperf3_json["end"]["streams"][0]["sender"]["mean_rtt"])
        self.retransmits = int(iperf3_json["end"]["streams"][0]["sender"]["retransmits"])

    def add_locust(self, locust_benchmark: Dict):
        get_request = locust_benchmark[0]
        num_request = get_request["num_requests"]
        average_response_time = 0
        for time, amount in get_request["response_times"].items():
            average_response_time += int(time) * amount
        average_response_time /= num_request

        self.httpMinResponseTime = get_request["min_response_time"]
        self.httpMaxResponseTime = get_request["max_response_time"]
        self.httpAverageResponseTime = average_response_time


class BenchmarkResults:
    def __init__(self):
        self.results = pandas.DataFrame()

    def add_result(self, benchmark_run: BenchmarkResult):
        self.results = self.results.append(
            {
                "server_node": benchmark_run.server_node,
                "client_node": benchmark_run.client_node,
                "mbps": benchmark_run.mbps,
                "cpu_host": benchmark_run.cpu_server,
                "cpu_client": benchmark_run.cpu_client,
                "mean_rtt": benchmark_run.mean_rtt,
                "retransmits": benchmark_run.retransmits,
                "httpMinResponseTime": benchmark_run.httpMinResponseTime,
                "httpMaxResponseTime": benchmark_run.httpMaxResponseTime,
                "httpAverageResponseTime": benchmark_run.httpAverageResponseTime,

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

                locust_benchmark = LocustBenchmark(client_node, server_node).run()
                benchmark.add_locust(locust_benchmark)

                self.benchmark_results.add_result(benchmark)

    def cleanup(self):
        IPerfBenchmark("", "").cleanup()
        LocustBenchmark("", "").cleanup()

    def json(self):
        return self.benchmark_results.json()
