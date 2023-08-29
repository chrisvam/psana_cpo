import glob
import os
import shutil
import stat
import time

import numpy as np
import os

class Dgram:
    def __init__(self,f):
        headerwords = 10
        self._header = np.fromfile(f,dtype=np.uint32,count=headerwords)
        self._xtcsize = 20
        self._payload = np.fromfile(f,dtype=np.uint8,count=self.extent()-self._xtcsize)
        #print('payload',self.extent(),len(self._payload))
    def clocklow(self): return self._header[0]
    def clockhigh(self): return self._header[1]
    def tslow(self): return self._header[2]&0xffffff
    def transitionId(self): return (self._header[2]>>24)&0x1f
    def tshigh(self): return self._header[3]
    def fiducials(self): return self.tshigh()&0x1ffff
    def env(self): return self._header[4]
    def dmg(self): return self._header[5]
    def srclog(self): return self._header[6]
    def srcphy(self): return self._header[7]
    def contains(self): return self._header[8]
    def extent(self): return self._header[9]
    def next(self): return self.extent()+self._xtcsize
    def data(self): return self._header
    def write(self,outfile):
        self._header.tofile(outfile)
        self._payload.tofile(outfile)

fnames = glob.glob('/sdf/data/lcls/ds/xpp/xpptut15/xtc/*0054*')
smdnames = glob.glob('/sdf/data/lcls/ds/xpp/xpptut15/xtc/smalldata/*0054*')
outfnames = ['/sdf/home/c/cpo/ana-4.0.51-py3/junkdata/'+os.path.split(f)[1]+'.inprogress' for f in fnames]
outsmdnames = ['/sdf/home/c/cpo/ana-4.0.51-py3/junkdata/smalldata/'+os.path.split(smd)[1]+'.inprogress' for smd in smdnames]

files = [open(f,'r') for f in fnames]
outfiles = [open(f,'w') for f in outfnames]
smdfiles = [open(f,'r') for f in smdnames]
outsmdfiles = [open(f,'w') for f in outsmdnames]

while 1:
    for fin,fout in zip(smdfiles+files,outsmdfiles+outfiles):
        dg = Dgram(fin)
        print(dg.transitionId(),dg.clocklow(),dg.clockhigh(),dg.fiducials())
        if dg.transitionId()==12: time.sleep(1)
        dg.write(fout)
