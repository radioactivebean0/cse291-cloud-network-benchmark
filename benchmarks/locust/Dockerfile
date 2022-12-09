FROM 888aaen/k8perf-locust:json
COPY locustfile.py .
ENTRYPOINT [ "python", "-m", "locust", "-f", "locustfile.py" ]
