#!/bin/bash

sudo service munge start
sudo service ssh start
sudo /etc/init.d/ssh start

tail -f /dev/null
