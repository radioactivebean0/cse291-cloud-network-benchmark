docker build . -t client
docker run --name locust -p 8089:8089 -d client
# pip install -r requirements.txt
# python -m locust --host http://localhost:80