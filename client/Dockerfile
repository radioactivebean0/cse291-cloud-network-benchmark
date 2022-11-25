FROM locustio/locust
COPY locustfile.py .
ENTRYPOINT [ "python", "-m", "locust", "-f", "locustfile.py", "-u", "10", "-r", "10", "--headless", "-t", "20s", "--host", "http://172.31.31.142:80", "--print-stats", "--csv", "exp" ]