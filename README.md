# Benchmark application

## Run the application
You can run the application in docker compose or native

Local:
#### Virtualenv
you can activate the virtualenv with the following command:
```bash
source bin/activate
```

```bash
# in one window
iperf3 -s
# in another window (make sure to activate the virtualenv)
python client localhost
```

Docker:
```bash
docker-compose up
```
