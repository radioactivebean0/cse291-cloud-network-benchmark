# Locust Benchmark application

## Run the application locally
Both the client and the server are running inside Docker containers

### Server
Prior to starting the server application, create a container network so that client containers and the server container can communicate.

```bash
docker network create --driver bridge locustnw
```

Then running the nginx image in the server container

```bash
docker run --name server -p 80:80 -d --network="host" nginx
```

This two command lines are put inside `run.sh`, you could also run

```bash
./run.sh
```

under the server folder.

### Client
The Dockerfile copies the host `locustfile.py` to the containers, therefore build the Dockerfile prior to running the client containers.

```bash
docker build . -t client
```

Then run the client container with specified container network

```bash
docker run -p 8089:8089 --network=locustnw client --host=http://localhost:80
```

And conduct experiments through `http://localhost:8089` (Only for local testing, experiments for cloud providers like AWS should use the ip address of the instance)

## Conduct experiments on AWS

### Server
To deploy the server pod, run

```bash
cd server
kubectl apply -f server.yaml
```

To stop a pod, run

```bash
kubectl delete -f server.yaml
```
### Client

The parameters of an experiment are defined inside the `Dockerfile` inside the `client` folder. To change the setting of an experiment, change the command line inside the `Dockerfile` and push the updated image to AWS ECR so that AWS EKS can pull images from client folders. See `client/build.sh` for more commands that push Docker images to AWS ECR. (Note: Remember to open Docker daemon process when pushing images to AWS ECR.)

To deploy a client pod, run

```bash
cd client
kubectl apply -f client.yaml
```

The deployment process will deploy a Job and it will start executing automatically. When a job is finished, run `kubectl logs {podname}` to retrieve the logs of the experiment inside console.

To stop a running experiment/client application, run

```bash
kubectl delete -f client.yaml
```
