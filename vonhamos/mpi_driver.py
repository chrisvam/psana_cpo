# run these commands in the "amoh1315" directory

# mpirun -n 2 python mpi_driver.py  exp=xpptut15:run=54 cspad -n 10
# in batch:
# bsub -q psanaq -n 2 -o %J.log -a mympi python mpi_driver.py exp=xpptut15:run=54

from mymaster import runmaster
from myclient import runclient

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
assert size>1, 'At least 2 MPI ranks required'
numClients = size-1

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("exprun", help="psana experiment/run string (e.g. exp=xppd7114:run=43)")
parser.add_argument("areaDetName", help="psana area detector name from 'print evt.keys()' (e.g. cspad)")
#parser.add_argument("-n","--noe",help="number of events, all events=0",default=-1, type=int)

args = parser.parse_args()

if rank==0:
    runmaster(numClients)
else:
    runclient(args)

MPI.Finalize()
