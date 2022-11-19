# Locust Benchmark application

## Run the application
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

