import glob
import os
import shutil
import stat

import numpy as np
import os

class Dgram:
    def __init__(self,f):
        headerwords = 10
        self._header = np.fromfile(f,dtype=np.uint32,count=headerwords)
        self._xtcsize = 20
        self._payload = np.fromfile(f,dtype=np.uint8,count=self.extent()-self._xtcsize)
        print 'payload',self.extent(),len(self._payload)
    def clocklow(self): return self._header[0]
    def clockhigh(self): return self._header[1]
    def tslow(self): return self._header[2]&0xffffff
    def transitionId(self): return (self._header[2]>>24)&0x1f
    def tshigh(self): return self._header[3]
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

infile = open('/reg/d/psdm/xpp/xpptut15/xtc/e665-r0151-s00-c00.xtc','r')
outfile = open('junk.xtc','w')
for i in range(6):
    dg = Dgram(infile)
    print dg.transitionId(),dg.clocklow(),dg.clockhigh()
    dg.write(outfile)
infile.close()
outfile.close()
