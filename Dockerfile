FROM ubuntu:20.04

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y python3-pip python3.8-dev

COPY etc/requirements.txt /tmp/requirements.txt

RUN python3 -m pip install -r /tmp/requirements.txt

CMD sleep inf
