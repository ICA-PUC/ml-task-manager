FROM ubuntu:20.04

RUN apt update -y && \
apt install munge -y && \
apt install vim -y && \ 
apt install build-essential -y && \
apt install git -y && \ 
apt-get install mariadb-server -y && \
apt install wget -y

ARG DEBIAN_FRONTEND=noninteractive


RUN apt install slurm-client -y
RUN apt install curl dirmngr apt-transport-https lsb-release ca-certificates -y
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -

RUN apt install sudo -y && \
    apt install python3.9 python3-pip -y && \ 
    useradd -m admin -s /usr/bin/bash -d /home/admin && \
    echo "admin:admin" | chpasswd && \
    adduser admin sudo && \
    echo "admin     ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN apt update -y && apt install nodejs -y && npm install -g configurable-http-proxy

COPY slurm.conf /etc/slurm-llnl/
COPY cgroup.conf /etc/slurm-llnl/
COPY docker-entrypoint.sh /etc/slurm-llnl/

WORKDIR /home/admin

RUN apt-get update -y && apt-get install -y openssh-server

RUN mkdir /var/run/sshd

EXPOSE 22

ENV USER admin
ENV SHELL bash

CMD ["/usr/sbin/sshd", "-D"]

ENTRYPOINT [ "/etc/slurm-llnl/docker-entrypoint.sh" ]
