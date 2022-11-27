import json
from typing import Literal
from time import sleep

import typer
from kubernetes import dynamic, config, utils
from kubernetes.client import api_client, ApiException
from kubernetes.dynamic.exceptions import NotFoundError
from kubernetes import client

from util import yaml

BENCHMARK_NAMESPACE = "network-benchmarks"

RESOURCE_TYPES = Literal["Job", "Service", "Deployment"]


class IPerfBenchmark():
    def __init__(self, client_node, server_node):
        self.client_node = client_node
        self.server_node = server_node
        self.client = dynamic.DynamicClient(
            api_client.ApiClient(configuration=config.load_kube_config())
        )
        self.k8api_client = client.ApiClient()

    def run(self):
        return self.iperf3_benchmark_kubernetes(self.client_node, self.server_node)

    @staticmethod
    def exists_in_kubernetes(resource, resource_type: RESOURCE_TYPES) -> bool:
        if resource_type == "Deployment":
            api = client.AppsV1Api()
            try:
                api.read_namespaced_deployment(name=resource["metadata"]["name"], namespace="default")
                return True
            except ApiException as e:
                if e.status == 404:
                    return False
                raise e
        elif resource_type == "Job":
            api = client.BatchV1Api()
            try:
                api.read_namespaced_job(name=resource["metadata"]["name"], namespace="default")
                return True
            except ApiException as e:
                if e.status == 404:
                    return False
                raise e

        elif resource_type == "Service":
            api = client.CoreV1Api()
            try:
                api.read_namespaced_service(name=resource["metadata"]["name"], namespace="default")
                return True
            except ApiException as e:
                if e.status == 404:
                    return False
                raise e

    def iperf3_benchmark_kubernetes(self, client_node, server_node):

        typer.echo("Running iperf3 benchmark on Kubernetes")
        typer.echo(f"Deploying iperf3 server to {server_node}")

        self.deploy_server(server_node)

        # Wait for server to be ready
        typer.echo("Waiting for server to be ready...")
        iperf3_server = {"meta": {"name": "iperf3-server"}}
        sleep(1)
        #self.wait_for_resource(iperf3_server, "Service")
        return self.deploy_client(client_node)

    def wait_for_resource(self, kube_resource, kind: RESOURCE_TYPES, namespace="default"):
        sleep(3)
        return
        name = ""
        if "metadata" in kube_resource.keys():
            name = kube_resource["metadata"]["name"]
        else:
            name = kube_resource["meta"]["name"]

        print(f"Waiting for {kind} {name} to be ready...")
        while True:
            try:
                print(f"Waiting for {kind} {kube_resource['meta']['name']} to be ready...")
                resp = self.client.resources.get(
                    api_version="v1", kind=kind
                ).get(name=name, namespace=namespace)
                print(resp.status.phase)
                if resp.status.phase == "Running":
                    break
            except NotFoundError as e:
                print(e)
                break
            except Exception as e:
                typer.echo(name)
                typer.echo(kube_resource["metadata"]["name"])
                typer.echo(kube_resource)
                typer.echo(e)
                typer.echo("Waiting for service to be ready...")
                sleep(2)

    def deploy_server(self, server_node):
        configs = yaml.load_to_dicts("bandwidth/iperf3-server.yaml")
        deployment, service = configs
        nodeSelector = {"kubernetes.io/hostname": server_node}
        deployment["spec"]["template"]["spec"]["nodeSelector"] = nodeSelector
        if self.exists_in_kubernetes(deployment, "Deployment"):
            self.delete_deployment(deployment)
            self.wait_for_resource(deployment, "Deployment")
        if self.exists_in_kubernetes(service, "Service"):
            self.delete_service(service)
            self.wait_for_resource(service, "Service")
        # Create deployment
        #self.wait_for_resource(service, "Service")

        utils.create_from_dict(self.k8api_client, deployment)
        print(f"\n[INFO] deployment `{deployment['metadata']['name']}` created.")
        utils.create_from_dict(self.k8api_client, service)
        print(f"\n[INFO] service `{service['metadata']['name']}` created.")

    def delete_deployment(self, kube_resource, namespace="default"):
        # Delete deployment
        apps_v1 = client.AppsV1Api()
        resp = apps_v1.delete_namespaced_deployment(
            name=kube_resource["metadata"]["name"],
            namespace=namespace,
            body=client.V1DeleteOptions(
                propagation_policy="Foreground", grace_period_seconds=5
            ),
        )
        print("Deployment deleted. status='%s'" % str(resp.status))

    def delete_job(self, kube_resource, namespace="default"):
        # Delete job
        batch_v1 = client.BatchV1Api()
        resp = batch_v1.delete_namespaced_job(
            name=kube_resource["metadata"]["name"],
            namespace=namespace,
            body=client.V1DeleteOptions(
                propagation_policy="Foreground", grace_period_seconds=5
            ),
        )

        print(f"\n[INFO] job `{kube_resource['metadata']['name']}` deleted.")

    def delete_service(self, kube_resource, namespace="default"):
        # Delete service
        core_v1 = client.CoreV1Api()
        resp = core_v1.delete_namespaced_service(
            name=kube_resource["metadata"]["name"],
            namespace=namespace,
            body=client.V1DeleteOptions(
                propagation_policy="Foreground", grace_period_seconds=5
            ),
        )
        print("Service deleted. status='%s'" % str(resp.status))

    def deploy_client(self, client_node):
        configs = yaml.load_to_dicts("bandwidth/iperf3-client.yaml")
        job = configs[0]
        nodeSelector = {"kubernetes.io/hostname": client_node}
        job["spec"]["template"]["spec"]["nodeSelector"] = nodeSelector
        if self.exists_in_kubernetes(job, "Job"):
            self.delete_job(job)
            typer.echo("Job already exists, deleting it...")
        # Create job
        sleep(2)
        utils.create_from_dict(self.k8api_client, job)
        print(f"\n[INFO] job `{job['metadata']['name']}` created.")

        # Wait for job to finish
        typer.echo("Waiting for job to finish...")
        self.wait_for_resource(job, "Job")

        # Get logs from job
        typer.echo("Getting logs from job...")
        return self.get_job_logs(job)

    def get_job_logs(self, kube_resource, namespace="default"):
        # wait for job to finish
        while True:
            batch_v1 = client.BatchV1Api()
            resp = batch_v1.read_namespaced_job_status(
                name=kube_resource["metadata"]["name"], namespace=namespace
            )
            if resp.status.succeeded == 1:
                break
            else:
                typer.echo("Waiting for job to finish...")
                sleep(2)

        # get pod with job selector
        api_instance = client.CoreV1Api()
        from kubernetes.client import V1PodList
        api_response: V1PodList = api_instance.list_namespaced_pod(namespace=namespace, label_selector="job-name=iperf3-client")
        job_pod_name = api_response.items[0].metadata.name
        # get logs from pod
        pod_log = api_instance.read_namespaced_pod_log(
            name=job_pod_name, namespace=namespace
        )

        pod_log_json = pod_log.replace("'", '"').replace("True", "true").replace("False", "false")

        benchmark_result = json.loads(pod_log_json)
        return benchmark_result
