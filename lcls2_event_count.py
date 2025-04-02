import glob
import sys
import subprocess
import os
exp=sys.argv[1]
myrunnum=int(sys.argv[2])
detname=sys.argv[3]
hutch=exp[:3]
datadir = os.environ['SIT_PSDM_DATA']
files=glob.glob(datadir+'/'+hutch+'/'+exp+'/xtc/smalldata/*r%4.4d*.xtc2'%myrunnum)
for f in files:
    output = subprocess.run(['detnames',f],capture_output=True)
    if detname in output.stdout.decode("utf-8"):
        cmd = f'xtcreader -s -f {f}'
        output = subprocess.run(cmd.split(),capture_output=True)
        print(output.stdout.decode('utf-8'))
        sys.exit(0)
print(f'Error: f{detname} detector not found')
sys.exit(-1)
