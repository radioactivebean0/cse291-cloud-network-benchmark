FROM python:3.10-alpine
RUN apk add --update iperf3 && rm -rf /var/cache/apk/*

# install python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy source code
COPY . /app
WORKDIR /app

## make results directory
RUN mkdir -p /app/results

# run the app
ENTRYPOINT ["python", "__main__.py"]

