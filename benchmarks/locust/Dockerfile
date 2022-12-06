FROM locustio/locust
COPY locustfile.py .
ENTRYPOINT [ "python", "-m", "locust", "-f", "locustfile.py", "-u", "500", "-r", "500", "--headless", "-t", "1m", "--host", "http://172.31.14.148:80", "--print-stats", "--csv", "exp" ]
