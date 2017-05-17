from psana import *
import time
from ImgAlgos.PyAlgos import PyAlgos

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

epix = {'exprun' : 'exp=xpptut15:run=260', 'dname': 'epix100a_diff',
        'peakselpars': {'npix_min':3, 'npix_max':1000, 'amax_thr':0,
                        'atot_thr':0, 'son_min':6},
        'v4r2pars': {'thr_low':6, 'thr_high':6, 'rank':3, 'r0':5, 'dr':2}}
cspad = {'exprun' : 'exp=cxitut13:run=10', 'dname': 'DscCsPad',
         'peakselpars': {'npix_min':2, 'npix_max':50, 'amax_thr':10,
                         'atot_thr':20, 'son_min':5},
         'v4r2pars': {'thr_low':10, 'thr_high':150, 'rank':4, 'r0':5, 'dr':0.05}}

for dset in [epix,cspad]:

    ds = DataSource(dset['exprun']+':idx')
    det = Detector(dset['dname'])
    run = ds.runs().next()
    times = run.times() 
    mylength = 80
    mytimes= times[rank*mylength:(rank+1)*mylength]

    tcalib = 0
    tpeak = 0
    alg = PyAlgos()
    alg.set_peak_selection_pars(**dset['peakselpars'])
    comm.Barrier()
    for nevent,t in enumerate(mytimes): 
        evt = run.event(t)
        raw = det.raw(evt) # fetch raw data here to avoid timing disk stuff
        # don't include the first event, which loads calibration stuff
        if nevent>0: t0 = time.time()
        calib = det.calib(evt)
        if nevent>0:
            t1 = time.time()
            tcalib += t1-t0
        peaks = alg.peak_finder_v4r2(calib,**dset['v4r2pars'])
        if nevent>0: 
            tpeak += time.time()-t1
            
    print dset['dname'],'calib/peak time per event:',tcalib/(len(mytimes)-1),tpeak/(len(mytimes)-1)
