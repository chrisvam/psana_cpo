import dgramCreate as dc
import numpy as np
import os
import h5py

config = {}
detname = 'epix10k2M'
dettype = 'epix10k'
serial_number = '1234'
namesid = 0

nameinfo = dc.nameinfo(detname,dettype,serial_number,namesid)
alg = dc.alg('raw',[0,0,1])

cydgram = dc.CyDgram()

fname = 'epix.xtc2'

f = open(fname,'wb')
h5f = h5py.File('epix10k2M.h5', 'r')
epix_dset = h5f['raw']
for nevt,epixraw in enumerate(epix_dset):
    my_data = [{'raw': epixraw[segment,:,:]} for segment in range(4)]

    for segment in range(4):
        nameinfo.namesId = segment
        cydgram.addDet(nameinfo, alg, my_data[segment], segment)
    timestamp = nevt
    if (nevt==0):
        transitionid = 2  # Configure
    else:
        transitionid = 12 # L1Accept
    xtc_bytes = cydgram.get(timestamp,transitionid)
    f.write(xtc_bytes)
f.close()
