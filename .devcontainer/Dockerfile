FROM ubuntu

ENV LANG C.UTF-8
ENV LC_CTYPE C.UTF-8
ENV PYTHONIOENCODING utf-8

USER root
SHELL ["/bin/bash", "-c"]

RUN \
  apt-get update && \
  apt-get install -y -q \
    curl \
    software-properties-common \
    build-essential \
    python3-pip \
  && \
# Install kicad
  add-apt-repository -y ppa:kicad/kicad-8.0-releases && \
  apt-get update && \
  apt-get install -y -q \
    kicad \
  && \
  pip3 install kikit --break-system-packages && \
# clean up
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*
