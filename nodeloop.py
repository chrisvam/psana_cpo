import subprocess
import os
import time
import sys
import datetime

nerr=0
msg=''
hosts = ['drp-srcf-cmp0%2.2d'%h for h in range(1,2)]
print hosts
for nhost,host in enumerate(hosts):
    cmd = 'ssh %s /sbin/ifconfig'%(host)
    try:
        result = subprocess.check_output(cmd, shell=True).decode('utf-8')
        result = result.split('\n')
        for line in result:
            if 'mtu' in line: print('****',host,line)
    except:
        nerr+=1
        msg+='*ERR %s\n'%host
msg+='*** Summary: found %d nodes with %d errors\n'%(len(hosts),nerr)
