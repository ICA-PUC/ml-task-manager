#!/bin/bash

export DATABASE_URL=ANY
export ATENA_ROOT=ANY
export NFS_ROOT=ANY
export SIF_PATH=ANY

cd app
fastapi dev main.py --port 8008
