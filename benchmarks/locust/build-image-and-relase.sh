#!/usr/bin/env bash
## Run this from the root folder of the project

VERSION="0.1.3"
echo "Building image version $VERSION"
docker build -t 888aaen/k8perf-locust-benchmark:$VERSION -t 888aaen/k8perf-locust-benchmark:latest -f benchmarks/locust/Dockerfile ./benchmarks/locust
docker push 888aaen/k8perf-locust-benchmark:$VERSION && docker push 888aaen/k8perf-locust-benchmark:latest
