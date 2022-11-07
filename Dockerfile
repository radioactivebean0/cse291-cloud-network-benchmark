FROM python:3.10-alpine
RUN apk add --update make automake gcc g++ subversion && rm -rf /var/cache/apk/*

# install python dependencies
COPY requirements.txt .
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

RUN mkdir -p images

# run the app
ENTRYPOINT ["python", "__main__.py"]

