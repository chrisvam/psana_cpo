from psana import *
import numpy as np
import sys
import argparse

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

def myiter(d1,d2,mykeys):
    for k, v in d1.items():
        if isinstance(v, dict):
            mykeys.append(k)
            myiter(v,d2[k],mykeys)
            del mykeys[-1]
        else:
            if type(v) is np.ndarray:
                if not np.array_equal(v,d2[k]):
                    if 'calibPixelConfigArray' in mykeys+[k]:
                        print "skipping calibPixelConfigArray"
                    else:
                        print(mykeys+[k],v,d2[k])
            else:
                if v!=d2[k]: print(mykeys+[k],v,d2[k])

parser = argparse.ArgumentParser(
    description = 'Compare the detector config in a pair of runs')
parser.add_argument('foo', default='Epix', help='Epix, Epix10ka, ...')
parser.add_argument('bar', default='Epix', help='Epix, Epix10ka, ...')
parser.add_argument('--detType', dest='detType', default='Epix', help='Epix, Epix10ka, ...')
parser.add_argument('--firstDetNumber', dest='d0', default=0, help='first camera number if multiple in run')
parser.add_argument('--secondDetNumber', dest='d1', default=0, type=int, help='second camera number if multiple in run')
args = parser.parse_args()
print args

expruns = [sys.argv[1],sys.argv[2]]
detNumbers = [args.d0, args.d1]
allresults = []
for detN, exprun in enumerate(expruns):
    ds = DataSource(exprun+':smd')
    ckeys = ds.env().configStore().keys()
    alias, source, eType = None, None, None
    cameraString = args.detType
    for key in ckeys:
        if cameraString in str(key.src()):
            if key.type() is None: continue
            alias, source, eType = key.alias(),key.src(),key.type()
            detNumber = eval(str(source).split('.')[-1].strip(')'))
            if detNumber == detNumbers[detN]:
                break
            else:
                eType = None
                continue

    if eType is None:
        print "couldn't find a(n) %s.%d in this run %s, bailing" %(args.detType, detNumbers[detN], exprun)
        sys.exit()

    eString = str(source)
    try:
        ecfg = ds.env().configStore().get(eType, source)
    except Exception, e:
        raise e

    result = {}
    if "Epix10ka2M" in eString:
        todict(ecfg,result,{'evr':1,'quad':4,'elemCfg':16,'adc':10,'asics':4})
    elif "Epix10kaQuad" in eString:
        todict(ecfg,result,{'evr':1,'quad':1,'elemCfg':16,'adc':10,'asics':4})
    elif "Epix10ka" in eString:
        todict(ecfg,result,{'evr':1, 'elemCfg':16,'adc':10,'asics':4})
    elif "Epix100" in eString:
        todict(ecfg,result,{'evr':1, 'elemCfg':16,'adc':10,'asics':4})
        ## maybe
    else:
        print "need to put something relevant here, bailing"
        sys.exit()
##        todict(ecfg,result,{'evr':1, 'elemCfg':16,'adc':10,'asics':4})

    allresults.append(result)

myiter(allresults[0],allresults[1],[])
