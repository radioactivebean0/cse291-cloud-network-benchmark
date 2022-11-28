FROM locustio/locust
COPY locustfile.py .
ENTRYPOINT [ "python", "-m", "locust", "-f", "locustfile.py", "-u", "1000", "-r", "1000", "--headless", "-t", "1m", "--host", "http://172.31.31.142:80", "--print-stats", "--csv", "exp" ]