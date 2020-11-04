from psana import DataSource
from psana.peakFinder.blobfinder import find_blobs_2d
import numpy as np
import os
os.environ['PS_SRV_NODES']='1'
ds = DataSource(exp='xpptut13',run=1,dir='/cds/home/c/cpo/git/psana_cpo/ued')
for myrun in ds.runs():
    det = myrun.Detector('epix10k2M')
    threshold = 2.0
    smallh5 = ds.smalldata(filename='blobs.h5')
    max_blobs=50
    for nevt,evt in enumerate(myrun.events()):
        image = det.raw.image(evt)
        if image is None: continue # check for missing data
        nblobs, x_blobs, y_blobs, energy_blobs = find_blobs_2d(image,threshold,2.0)
        # currently only support fixed-length arrays in h5
        if nblobs>max_blobs:
            print('too many blobs')
            continue
        x      = np.zeros((max_blobs),dtype=np.float32)
        y      = np.zeros((max_blobs),dtype=np.float32)
        energy = np.zeros((max_blobs),dtype=np.float32)
        x[:nblobs]     = x_blobs
        y[:nblobs]     = y_blobs
        energy[:nblobs]= energy_blobs
        smallh5.event(evt, nblobs=nblobs, x=x, y=y, energy=energy)
        print('Event',nevt,'found',nblobs,'blobs')
    smallh5.done()
    
