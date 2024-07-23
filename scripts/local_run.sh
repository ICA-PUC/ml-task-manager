#!/bin/bash

export DATABASE_URL=ANY
export ATENA_ROOT=ANY

uvicorn app.main:app --host 0.0.0.0 --port 8008
