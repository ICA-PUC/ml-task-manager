#!/bin/sh

docker pull postgres:15-alpine

cd app/docker
docker build -t humblebeaver/ml-task-manager .

cd ../../db/docker
bash ./buildDockerImage.sh -v 19.3.0 -e
