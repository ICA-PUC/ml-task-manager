#!/bin/bash

sudo sed -i "s/REPLACE_IT/CPUs=$(nproc)/g" /etc/slurm-llnl/slurm.conf

sudo service munge start
sudo service slurmctld start

sudo service ssh start
sudo /etc/init.d/ssh start

tail -f /dev/null
