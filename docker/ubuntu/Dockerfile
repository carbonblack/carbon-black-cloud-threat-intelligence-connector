from ubuntu:18.04
MAINTAINER cb-developer-network@vmware.com

COPY . /app
WORKDIR /app

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip
RUN apt-get install -y python3-isodate
RUN apt-get install -y python3-iso8601
RUN pip3 install -r requirements.txt
RUN pip3 install .
