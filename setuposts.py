import sys
import subprocess
import errno    
import os

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

filesystem = sys.argv[1]
assert os.path.isdir(filesystem)
import subprocess
batcmd="lfs osts "+filesystem
result = subprocess.check_output(batcmd, shell=True)
lines = result.split('\n')
osts = []
for line in lines:
    if ':' in line:
        field = line.split(':')[0]
        try:
            osts.append(int(field))
        except:
            pass
print 'Found OSTs:',osts
for ost in osts:
    xtcdirname = os.path.join(filesystem,'test/psana_batch/ost%x'%ost)
    idxdirname = os.path.join(xtcdirname,'index')
    print 'Setting up',xtcdirname
    assert not os.path.isdir(xtcdirname) # make sure it doesn't already exist
    mkdir_p(idxdirname)
    xtcfile = 'e307-r0999-s00-c00.xtc'
    idxfile = xtcfile+'.idx'
    xtcfullpath = os.path.join(xtcdirname,xtcfile)
    idxfullpath = os.path.join(idxdirname,idxfile)
    os.system('lfs setstripe -c 1 -i %d %s'%(ost,xtcfullpath))
    os.system('lfs setstripe -c 1 -i %d %s'%(ost,idxfullpath))
    os.system('cp /reg/data/ana02/test/psana_batch/%s %s'%(xtcfile,xtcfullpath))
    os.system('cp /reg/data/ana02/test/psana_batch/index/%s %s'%(idxfile,idxfullpath))
    os.system('chmod +r -R '+xtcdirname)
