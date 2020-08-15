import os
import glob
import sys

expt = sys.argv[1]
hutch = expt[0:3]

dir = '/reg/d/psdm/'+hutch+'/'+expt+'/xtc/'

if len(sys.argv)==3:
    run = int(sys.argv[2])
    files = glob.glob(dir+'/*r%4.4d*.xtc'%run) # specific runs
elif len(sys.argv)==2:
    files = glob.glob(dir+'/*.xtc') # all files
else:
    print 'Incorrect number of arguments'
    sys.exit()

print files

for file in files:
    basename = os.path.basename(file).split('.')[0]
    smddir = dir+'/smalldata/'
    if not os.path.exists(smddir):
        print 'Creating directory',smddir
        os.mkdir(smddir)
    smdfile = smddir+basename+'.smd.xtc'
    if os.path.isfile(smdfile):  # skip existing files
        continue
    cmd = '/usr/local/bin/bsub -q psanaq -o ~/logs/%J.log smldata -f '+file+' -o ' + smdfile + ' >& /dev/null'
    os.system(cmd)
