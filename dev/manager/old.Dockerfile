FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN rm -f /etc/apt/sources.list.d/*.list

RUN apt-get update && \
    apt-get install -y \
    openssh-server \
    munge \
    vim \
    build-essential \
    git \
    mariadb-server \
    wget \
    slurmd \
    slurm-client \
    curl \
    dirmngr \
    apt-transport-https \
    lsb-release \
    ca-certificates \
    sudo \
    python3.9 \
    python3-pip \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/* 

RUN curl -sL https://deb/nodesource.com/setup_12.x | bash -
RUN useradd -m admin -s /usr/bin/bash -d /home/admin && echo "admin:admin" | chpasswd && \
    adduser admin sudo && \
    echo "admin     ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN npm install -g configurable-http-proxy

RUN mkdir /var/run/sshd
# Set root password for SSH access
RUN echo 'root:root123' | chpasswd
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

COPY slurm.conf /etc/slurm-llnl/
COPY cgroup.conf /etc/slurm-llnl/
COPY docker-entrypoint.sh /etc/slurm-llnl/

# WORKDIR /home/admin

EXPOSE 22

# ENV USER admin
# ENV SHELL bash

# RUN sudo service munge start
CMD [ "/etc/slurm-llnl/docker-entrypoint.sh" ]
