FROM python:3.10-alpine
RUN apk add --update iperf3
RUN apk add --update make automake gcc g++ subversion python3-dev && rm -rf /var/cache/apk/*

# install python dependencies
COPY requirements.txt .
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

# copy source code
COPY . /app
WORKDIR /app

## make results directory
RUN mkdir -p /app/results
RUN mkdir -p /app/images

# run the app
ENTRYPOINT ["python", "__main__.py"]

