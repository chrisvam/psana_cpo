from psana import DataSource
import numbers
import numpy as np

def iter(myitem,name):
    if (isinstance(myitem,dict)):
        pass # ignore the meta-data for enum's.
    elif (isinstance(myitem,np.ndarray) or isinstance(myitem,numbers.Number) or isinstance(myitem,str)):
        print(name,':\n',myitem)
        name = '.'.join(name.split('.')[:-1])
    else:
        attrs = [a for a in dir(myitem) if not a.startswith('_')]
        assert len(attrs)>0,myitem
        for attr in attrs:
            name+='.'+attr
            iter(getattr(myitem,attr),name)
            name = '.'.join(name.split('.')[:-1])

def dump(dg):
    attrs = [a for a in dir(dg) if not a.startswith('_') and a not in ['service','timestamp','software']]
    for attr in attrs:
        det = getattr(dg,attr)
        if isinstance(det,dict):
            for segment,myitem in det.items():
                iter(myitem,attr+'.'+str(segment))

ds = DataSource(files='data.xtc2')
myrun = next(ds.runs())

print('******** configure')
dump(myrun.configs[0])
for nevt,evt in enumerate(myrun.events()):
    print('******** event',nevt)
    dump(evt._dgrams[0])
    break
