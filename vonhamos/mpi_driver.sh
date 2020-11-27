#!/bin/bash
# run like this:
# `which mpirun` --oversubscribe -H daq-xcs-mon06,daq-xcs-mon07 -n 3 ./mpi_driver.sh
source /reg/g/psdm/etc/psconda.sh
cd /reg/neh/home/cpo/ipsana/xcs/
python -u mpi_driver.py shmem=psana.0:stop=no epix_1
#python -u mpi_driver.py exp=xcslt8717:run=227,228:smd epix_1
