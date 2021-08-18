from psana import DataSource
from psana import container
import numpy as np
import argparse
parser.add_argument("Experiment", help="Stick the detector name and number here (rixx43518)")
parser.add_argument("Runnumber", help="Run number goes here (341)")
parser.add_argument("Detector",)
parser.add_argument("--Segment", help="Enter the specific... segments you want to run in this format: x,y,z,etc,etc")
args=parser.parse_args()
experiment=str(args.Experiment)
runnum=int(args.runnumber)
ds = DataSource(exp=experiment,run=runnum)
myrun = next(ds.runs())
timing = myrun.Detector(args.Detector)
cfgs = timing.raw._seg_configs()
segmentrawlist=args.Segment
segmentlist=segmentrawlist.split(",")
print(cfgs)
result=cfgs
# goal: have a routine that print_config('timing')
# discussed here: https://confluence.slac.stanford.edu/display/PSDMInternal/Raw+Data+Python+Interface
# in particular this part: detname[nSegment].drpClassName.attr1.attr2...
def recursivechecks(obj, attrlist):
    allattrs = dir(obj)
    usefulattrs=[]
    for item in allattrs:
        if "_" not in item:
            usefulattrs.append(item)
    #alternativeattrs=obj.__dict__
    #print(alternativeattrs, "alternativeattrs")
    for attr in usefulattrs:
        val = getattr(obj, attr)
        attrlist.append(attr)
        #If attr is int, float, or array, print. If it's a container, recurse, otherwise, sit around
        #Look up how to check types of objects, especially a numpy array
        if type(val) in [int, float, np.ndarray, str]:
            printhere=joiner.join(attrlist)
            print(printhere, val)
        elif type(val) is container.Container:
            recursivechecks(val, attrlist)
        attrlist.pop(-1)
"""
for myobj in cfgs.values():
    print(myobj)
    attrlist=[]
    if type(args.Segment) is list:
        for seg in args.Segment:
            for key in cfgs:
                if segmentvalue==key:
                    recursivechecks(myobj, attrlist)
    else:
        for key in cfgs:
            recursivechecks(myobj, attrlist)
"""
if type(segmentlist) is list and segmentlist!=None:
    for seg in segmentlist:
        attrlist=[]
        recursivechecks(cfgs[seg], attrlist)
else:
    for myobj in cfgs.values():
        attrlist=[]
        recursivechecks(myobj, attrlist)
    
