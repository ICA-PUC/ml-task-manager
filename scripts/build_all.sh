#!/bin/sh

docker pull postgres:15-alpine

cd app/docker
docker build -t humblebeaver/ml-task-manager .

cd ../../dev/manager
docker build -t managerslurm .

cd ../server/master
docker build -t masterslurm .

cd ../node
docker build -t nodeslurm .