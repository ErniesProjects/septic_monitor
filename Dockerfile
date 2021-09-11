FROM python:3.8

COPY septic_monitor /opt/sm/septic_monitor

COPY setup.py /opt/sm/setup.py

WORKDIR /opt/sm

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y install build-essential python3-smbus

RUN python -m pip install pip setuptools wheel --upgrade && \
    CFLAGS=-fcommon python -m pip install -e .