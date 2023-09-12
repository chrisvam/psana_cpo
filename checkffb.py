import subprocess
import os
import time
import sys
import datetime

def gethosts(queue):
    openhosts = []
    otherhosts = []
    result = subprocess.check_output('sinfo -N -p %s'%queue, shell=True).decode('utf-8')
    for line in result.split('\n')[1:]:
        if ' idle' in line or ' alloc' in line or ' mix' in line or ' drain' in line or ' down' in line:
            fields = line.split()
            if len(fields) == 0: continue
            if ' drain' not in line and ' down' not in line:
                openhosts.append(fields[0])
            else:
                otherhosts.append(fields[0])
    openhosts.sort()
    otherhosts.sort()
    return openhosts,otherhosts

fname='/sdf/data/lcls/drpsrcf/ffb/test/psana_batch/e307-r0999-s00-c00.xtc'

openhosts,otherhosts = gethosts('milano')
nerr=0
for nhost,host in enumerate(openhosts):
    cmd = 'ssh %s ls %s'%(host,fname)
    try:
        result = subprocess.check_output(cmd, shell=True).decode('utf-8')
        #print('****',host,result)
    except:
        nerr+=1
        print('*ERR',host)
print('--- Summary: found',len(openhosts),'nodes with',nerr,'errors')

