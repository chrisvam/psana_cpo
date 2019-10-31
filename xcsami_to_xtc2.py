import dgramCreate as dc
import numpy as np
import os
import h5py

config = {}
detname = 'xpp_ipm4'
dettype = 'ipm'
serial_number = '1234'
namesid = 0

nameinfo = dc.nameinfo(detname,dettype,serial_number,namesid)
alg = dc.alg('raw',[0,0,1])

cydgram = dc.CyDgram()

fname = 'xcsami.xtc2'

f = open(fname,'wb')
h5f = h5py.File('/reg/d/psdm/xcs/xcslq2515/scratch/snelson/xcslq2515_Run061.h5', 'r')
ipm4 = h5f['ipm4']['sum']
for nevt,ipmval in enumerate(ipm4):
    my_data = {
        'sum': ipmval,
    }

    cydgram.addDet(nameinfo, alg, my_data)
    timestamp = nevt
    pulseid = nevt
    if (nevt==0):
        transitionid = 2  # Configure
    else:
        transitionid = 12 # L1Accept
    xtc_bytes = cydgram.get(timestamp,pulseid,transitionid)
    f.write(xtc_bytes)
    if nevt == 4: break
f.close()
