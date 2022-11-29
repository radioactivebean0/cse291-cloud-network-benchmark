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

### Run iperf 3 benchmark on kubernetes
There are two files in the folder `bandwidth`:
- the server `iperf3-server.yaml`
- the client `iperf3-client.yaml`

Right now i have nodes specified in both deployments. To change the hostname in them:
- change line 36 in `bandwidth/iperf3-server.yaml`
- change line 16 in `bandwidth/iperf3-client.yaml`

#### Running benchmark
First open two terminals. In the first deploy the server, and attach is logs.
The server have to de deployed before the client by running the following command:
```bash
kubectl apply -f bandwidth/iperf3-server.yaml
```
Then attach the logs
```bash
kubectl logs -f -l io.kompose.service=server
```

In the second terminal, deploy the client by running the following command:
```bash
kubectl apply -f bandwidth/iperf3-client.yaml
```

Now you should see something in the first terminal.

To rerun the benchmark first delete the job, and then create it again. You do this by running:
```bash
kubectl delete -f bandwidth/iperf3-client.yaml
kubectl apply -f bandwidth/iperf3-client.yaml
```