from psana import *
import time
import argparse

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

parser = argparse.ArgumentParser()
parser.add_argument('--assem', dest='assem', action='store_true', help='Select "assem" mode (versus "image" mode)')
parser.add_argument('--cfg', dest='cfg', action='store_true', help='Select old-style psana .cfg file mode (versus "AreaDetector" mode)')
args = parser.parse_args()
if args.assem:
    if rank==0: print 'Accessing assembled data'
else:
    if rank==0: print 'Accessing unassembled data'
if args.cfg:
    if rank==0: print 'Using old-style psana configuration file'
    src = Source('DetInfo(Camp.0:pnCCD.0)')
else:
    if rank==0: print 'Using new-style AreaDetector data access'

if args.cfg:
    if args.assem:
        setConfigFile('pnccdImage.cfg')
    else:
        setConfigFile('pnccdCalib.cfg')

ds = DataSource('exp=amoj4115:run=222:idx')
det = Detector('pnccdFront',ds.env())
run = ds.runs().next()
times = run.times() 
mylength = 20
mytimes= times[rank*mylength:(rank+1)*mylength]
comm.Barrier()

for nevent_me,t in enumerate(mytimes): 
    evt = run.event(t)
    if args.cfg:
        if args.assem:
            img = evt.get(ndarray_float64_2,src,'image')
        else:
            img = evt.get(ndarray_float64_2,src,'calibrated')
    else:
        if args.assem:
            img = det.image(evt)
        else:
            calib = det.calib(evt)
    # start after first event to avoid measuring "setup" time
    if nevent_me ==0: tstart = time.time()

print rank,'Time per event:',(time.time()-tstart)/(len(mytimes)-1)
