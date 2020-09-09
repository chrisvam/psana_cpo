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

h5f = h5py.File('epix10k2M.h5', 'r')
epix_dset = h5f['raw']
ids = h5f['ids']
idlist = ids[0].decode().split('_')

fname = 'epix.xtc2'
f = open(fname,'wb')
for nevt,epixraw in enumerate(epix_dset):
    my_data = [{'raw': epixraw[segment,:,:]} for segment in range(4)]

    for segment in range(4):
        nameinfo.namesId = segment
        nameinfo.detId = idlist[segment].encode()
        cydgram.addDet(nameinfo, alg, my_data[segment], segment)
    timestamp = nevt
    if (nevt==0):
        transitionid = 2  # Configure
    else:
        transitionid = 12 # L1Accept
    xtc_bytes = cydgram.get(timestamp,transitionid)
    f.write(xtc_bytes)
f.close()
