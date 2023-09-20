import glob
import sys
import os
exp=sys.argv[1]
myrunnum=int(sys.argv[2])
hutch=exp[:3]
files=glob.glob('/sdf/data/lcls/ds/'+hutch+'/'+exp+'/xtc/smalldata/*r%4.4d*.xtc2'%myrunnum)
for f in files:
    os.system('detnames %s'%f)
    os.system('xtcreader -f %s | grep L1Accept | wc -l'%f)
