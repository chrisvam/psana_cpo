import glob
import os
import shutil
import stat

import numpy as np
import os

class Dgram:
    def __init__(self,f):
        self._nwords = 10
        self._data = np.fromfile(f,dtype=np.uint32,count=self._nwords)
        self.f = f
    def write(self):
        self._data.tofile(self.f)
    def clocklow(self): return self._data[0]
    def clockhigh(self): return self._data[1]
    def tslow(self): return self._data[2]
    def tshigh(self): return self._data[3]
    def env(self): return self._data[4]
    def setenv(self,value): self._data[4]=value
    def dmg(self): return self._data[5]
    def srclog(self): return self._data[6]
    def srcphy(self): return self._data[7]
    def contains(self): return self._data[8]
    def extent(self): return self._data[9]
    def next(self): return self.extent()+5*4 # 5*4 is size of Xtc
    def data(self): return self._data

def fixRunNumber(fname):
    fstat = os.stat(fname).st_mode
    os.chmod(fname, fstat | stat.S_IWUSR)
    # to fix the run number in the "env" field of the beginrun datagram
    newrun = int(os.path.basename(fname).split('-')[1][1:])
    f = open(fname,'r+')
    configdg = Dgram(f)
    f.seek(configdg.next())
    beginrunoffset = f.tell()
    beginrundg = Dgram(f)
    f.seek(beginrunoffset)
    beginrundg.setenv(newrun)
    beginrundg.write()

    #check
    f.seek(beginrunoffset)
    newbeginrundg = Dgram(f)
    #print beginrundg.data()
    #print newbeginrundg.data()
    assert newbeginrundg.env()==newrun, 'Read incorrect run number %d %d'%(newrun,newbeginrundg.env())
    f.close()
    os.chmod(fname, fstat)
