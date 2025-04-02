import glob
import sys
import subprocess
exp=sys.argv[1]
myrunnum=int(sys.argv[2])
hutch=exp[:3]
files=glob.glob('/sdf/data/lcls/ds/'+hutch+'/'+exp+'/xtc/smalldata/*r%4.4d*.xtc2'%myrunnum)
for f in files:
    output = subprocess.run(['detnames',f],capture_output=True)
    if 'timing' in output.stdout.decode("utf-8"):
        cmd = f'xtcreader -C -f {f}'
        output = subprocess.run(cmd.split(),capture_output=True)
        print(output.stdout.decode('utf-8'))
        sys.exit(0)
print('Error: timing detector not found')
sys.exit(-1)
