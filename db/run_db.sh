#!/bin/sh

RFOLDER="$(pwd)"

docker run --name dtwin-oracle_db -d \
    -v $RFOLDER/oradata:/opt/oracle/oradata \
    -v $RFOLDER/sql:/opt/oracle/scripts/setup \
    -p 1521:1521 \
    -p 5500:5500 \
    -e ORACLE_PWD=Digital_twin_db42 \
    -e ORACLE_CHARACTERSET=AL32UTF8 \
    oracle/database:19.3.0-ee
