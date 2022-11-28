from time import sleep

import typer

from kubernetes_integration import KubernetesIntegration, RESOURCE_TYPES
from util import yaml

BENCHMARK_NAMESPACE = "network-benchmarks"


class IPerfBenchmark:
    def __init__(self, client_node, server_node):
        self.client_node = client_node
        self.server_node = server_node
        self.k8 = KubernetesIntegration(namespace="default")
    def run(self):
        return self.iperf3_benchmark_kubernetes(self.client_node, self.server_node)

    def iperf3_benchmark_kubernetes(self, client_node, server_node):

        typer.echo("Running iperf3 benchmark on Kubernetes")
        typer.echo(f"Deploying iperf3 server to {server_node}")

        self.deploy_server(server_node)

        # Wait for server to be ready
        typer.echo("Waiting for server to be ready...")
        iperf3_server = {"meta": {"name": "iperf3-server"}}
        self.k8.wait_for_resource(iperf3_server, "Service")
        return self.deploy_client(client_node)

    def deploy_server(self, server_node):
        configs = yaml.load_to_dicts("bandwidth/iperf3-server.yaml")
        deployment, service = configs
        nodeSelector = {"kubernetes.io/hostname": server_node}
        deployment["spec"]["template"]["spec"]["nodeSelector"] = nodeSelector
        if self.k8.exists_in_kubernetes(deployment, "Deployment"):
            self.k8.delete_deployment(deployment)
            self.k8.wait_for_deletetion(deployment, "Deployment")
        if self.k8.exists_in_kubernetes(service, "Service"):
            self.k8.delete_service(service)
            self.k8.wait_for_resource(service, "Service")
        # Create deployment
        # self.wait_for_resource(service, "Service")

        self.k8.create_from_dict(deployment)
        print(f"\n[INFO] deployment `{deployment['metadata']['name']}` created.")
        self.k8.create_from_dict(service)
        print(f"\n[INFO] service `{service['metadata']['name']}` created.")

    def deploy_client(self, client_node):
        configs = yaml.load_to_dicts("bandwidth/iperf3-client.yaml")
        job = configs[0]
        nodeSelector = {"kubernetes.io/hostname": client_node}
        job["spec"]["template"]["spec"]["nodeSelector"] = nodeSelector
        if self.k8.exists_in_kubernetes(job, "Job"):
            self.k8.delete_job(job)
            typer.echo("Job already exists, deleting it...")
        # Create job
        sleep(2)
        self.k8.create_from_dict(job)
        print(f"\n[INFO] job `{job['metadata']['name']}` created.")

        # Wait for job to finish
        typer.echo("Waiting for job to finish...")
        self.k8.wait_for_resource(job, "Job")

        # Get logs from job
        typer.echo("Getting logs from job...")
        return self.k8.get_job_logs(job)
