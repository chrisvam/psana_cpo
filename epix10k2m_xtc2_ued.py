import dgramCreate as dc
import numpy as np
import os
import h5py

config = {}
detname = 'epix10k2M'
dettype = 'opal'
serial_number = '1234'
namesid = 0

nameinfo = dc.nameinfo(detname,dettype,serial_number,namesid)
alg = dc.alg('raw',[2,0,0])

cydgram = dc.CyDgram()

h5f = h5py.File('epix10k2M_ued.h5', 'r')
epix_dset = h5f['raw']

runinfo_detname = 'runinfo'
runinfo_dettype = 'runinfo'
runinfo_detid = ''
runinfo_namesid = 255 # mirroring psdaq/drp/drp.hh
runinfo_nameinfo = dc.nameinfo(runinfo_detname,runinfo_dettype,
                               runinfo_detid,runinfo_namesid)
runinfo_alg = dc.alg('runinfo',[0,0,1])
runinfo_data = {
    'expt': 'tstx00417',
    'runnum': 14
}

fname = 'epix_ued.xtc2'
f = open(fname,'wb')
for nevt,epixraw in enumerate(epix_dset):
    my_data = {'image': epixraw}

    segment = 0
    nameinfo.namesId = segment
    nameinfo.detId = ''.encode()
    cydgram.addDet(nameinfo, alg, my_data, segment)
    timestamp = nevt

    # only do this for the first two dgrams: name info for config, and
    # the runinfo data for beginrun
    if nevt<2: cydgram.addDet(runinfo_nameinfo, runinfo_alg, runinfo_data)

    if (nevt==0):
        transitionid = 2  # Configure
    elif (nevt==1):
        transitionid = 4  # BeginRun
    elif (nevt==99):
        transitionid = 5  # EndRun
    else:
        transitionid = 12 # L1Accept
    xtc_bytes = cydgram.get(timestamp,transitionid)
    f.write(xtc_bytes)
    if nevt==99: break
f.close()
