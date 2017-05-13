from psana import *
import time
import argparse
from ImgAlgos.PyAlgos       import PyAlgos

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

parser = argparse.ArgumentParser()
parser.add_argument('--assem', dest='assem', action='store_true', help='Select "assem" mode (versus "image" mode)')
args = parser.parse_args()
if args.assem:
    if rank==0: print 'Accessing assembled data'
else:
    if rank==0: print 'Accessing unassembled data'

#ds = DataSource('exp=amoj4115:run=222:idx')
#det = Detector('pnccdFront')
#ds = DataSource('exp=xpptut15:run=260:idx')
#det = Detector('epix100a_diff')
ds = DataSource('exp=cxitut13:run=10:idx')
det = Detector('DscCsPad')
run = ds.runs().next()
times = run.times() 
mylength = 20
mytimes= times[rank*mylength:(rank+1)*mylength]
comm.Barrier()

ttot = 0
alg = PyAlgos()
# for epix
#alg.set_peak_selection_pars(npix_min=3, npix_max=1000, amax_thr=0, atot_thr=0, son_min=6)
# for cspad
alg.set_peak_selection_pars(npix_min=2, npix_max=50, amax_thr=10, atot_thr=20, \
son_min=5)
for nevent,t in enumerate(mytimes): 
    evt = run.event(t)
    raw = det.raw(evt) # fetch raw data here to avoid timing disk stuff
    # don't include the first event, which loads calibration stuff
    if nevent>0: tstart = time.time()
    if args.assem:
        img = det.image(evt)
    else:
        calib = det.calib(evt)
        #for epix
        #peaks_arc = alg.peak_finder_v4r2(calib, thr_low=6, thr_high=6, rank=3, r0=5, dr=2)
        #for cspad
        #alg.peak_finder_v4r2(calib,thr_low=10, thr_high=150, rank=4, r0=5, dr=0.05)
    if nevent>0: ttot += time.time()-tstart

print rank,'Time per event:',ttot/(len(mytimes)-1)
