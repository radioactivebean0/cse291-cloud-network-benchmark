FROM locustio/locust
COPY locustfile.py .
ENTRYPOINT [ "python", "-m", "locust", "-f", "locustfile.py" ]