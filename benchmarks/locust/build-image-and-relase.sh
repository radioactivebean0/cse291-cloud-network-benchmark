#!/usr/bin/env sh
## Run this from the root folder of the project

$VERSION= $( python3 -c "import locust; print(locust.__version__)" ) . "json"
docker build -t 888aaen/k8perf-locust-benchmark:$VERSION -t 888aaen/k8perf-locust-benchmark:latest -f benchmarks/locust/Dockerfile ./benchmarks/locust
docker push 888aaen/k8perf-locust-benchmark:$VERSION && docker push 888aaen/k8perf-locust-benchmark:latest
