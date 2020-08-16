from __future__ import print_function
from psana import *
import numpy as np
import sys

def todict(obj,result,special_list):
    attrs = [a for a in dir(obj) if not a.startswith('_')]
    for a in attrs:
        attr = getattr(obj,a)
        if a not in special_list:
            # the straightforward "fundamental type" attributes
            if callable(attr):
                result[a]=attr()
            else:
                result[a]=attr
        else:
            # the complex attributes
            result[a]={}
            nspecial = special_list[a]
            if nspecial == 1:  # special case if we only have 1
                result[a][0]={}
                todict(attr(),result[a][0],special_list)
            else:
                for i in range(nspecial):
                    result[a][i]={}
                    todict(attr(i),result[a][i],special_list)

class compare:
    def __init__(self,d1,d2):
        self.mykeys=[]
        self.ncheck=0
        self.iterate(d1,d2)
    def iterate(self,d1,d2):
        for k, v in d1.items():
            if isinstance(v, dict):
                self.mykeys.append(k)
                self.iterate(v,d2[k])
                del self.mykeys[-1]
            else:
                self.ncheck+=1
                if type(v) is np.ndarray:
                    if not np.array_equal(v,d2[k]): print(self.mykeys+[k],v,d2[k])
                else:
                    if v!=d2[k]: print(self.mykeys+[k],v,d2[k])

expruns = [sys.argv[1],sys.argv[2]]
allresults = []
for exprun in expruns:
    ds = DataSource(exprun+':smd')
    ecfg = ds.env().configStore().get(Epix.Config10ka2MV1,
                                      Source('DetInfo(MfxEndstation.0:Epix10ka2M.0)'))
    result = {}
    todict(ecfg,result,{'evr':1,'quad':4,'elemCfg':16,'adc':10,'asics':4})
    allresults.append(result)

cmp = compare(allresults[0],allresults[1])
print('Checked',cmp.ncheck,'values')
