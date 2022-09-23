import psana
import numpy as np
import sys
import socket
import os

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-d','--dir',nargs='+', help="list of directories",required=True)
args = parser.parse_args()

for d in args.dir:
    nerror=0
    if not os.path.isfile(d+'/e307-r0999-s00-c00.xtc'):
        print('*** Error: Host',socket.gethostname(),'cannot access directory',d)
        nerror+=1
    if nerror:
        sys.exit()

for d in args.dir:
    firsttime = True

    ds = psana.DataSource('dir=%s:exp=xcstut13:run=999:idx'%d)
    src = psana.Source('DetInfo(XcsBeamline.0:Princeton.0)')
    maxEventsPerNode=2

    for run in ds.runs():
        times = run.times()
        mylength = len(times)/size
        if mylength>maxEventsPerNode: mylength=maxEventsPerNode
        mytimes= times[rank*mylength:(rank+1)*mylength]
        for i in range(mylength):
            evt = run.event(mytimes[i])
            if evt is None:
                print('*** event fetch failed')
                continue
            cam = evt.get(psana.Princeton.FrameV1,src)
            if cam is None:
                print('*** failed to get cam')
                continue
            if firsttime:
                sum=cam.data().astype(np.float)
                firsttime=False
            else:
                sum+=cam.data()

    sumall = np.empty_like(sum)

    #sum the images across mpi cores
    comm.Reduce(sum,sumall)

    if rank==0:
        print('dir:',d)
        print('sum:',np.sum(sumall))

MPI.Finalize()
