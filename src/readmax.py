import numpy as np
from psana import *

class readmax ( object ) :
    def __init__ ( self) :
        self.m_src = self.configSrc('source')
        self.maxarr = np.load('/reg/neh/home1/cpo/ipsana/exp=cxib2313:run=115_max.npy')

    def event(self,evt,env):
        evt.put(self.maxarr,self.m_src,'max')
