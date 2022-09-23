#!/usr/bin/env python

"""
If this script is run with:
- 0 arguments, jobs will be run on all open batch nodes.
- 2 node-name arguments, the job will be run only on that pair (with no
  automated checking of results or email).  the two nodenames can be
  identical to test only one node.
- 1 argument "checkdirs" subprocesses will be spawned that "ls" all
  the directories to be tested.  "ps" can then be used to see if any of
  them hang.
"""

import subprocess
import os
import time
import sys
import datetime

ana03 = ['/reg/data/ana03/test/psana_batch/ost%x' % i for i in range(1,19)]
ana15 = ['/reg/data/ana15/test/psana_batch/ost%x' % i for i in range(1,7)]

xtc_ana = [
    '/reg/data/ana01/test/psana_batch',
    '/reg/data/ana02/test/psana_batch',
]

xtc_ana+=ana03

calib_ana = [
    # Leave out ana13 because we get intermittent stale file handle issues in drpsrcf
    #'/reg/data/ana13/test/psana_batch',
    '/reg/data/ana15/test/psana_batch',
    '/reg/data/ana16/test/psana_batch',
]

calib_ana+=ana15

all_ana = xtc_ana + calib_ana

ffb = ['/cds/data/drpsrcf/temp/psana_batch']

timeLimitMinutes = 2
headroomMinutes = 2
queues = ['psfehq'  , 'psanaq', 'anaq']
dirs =   [all_ana, all_ana, calib_ana+ffb]

logdir = '/reg/g/psdm/utils/batchtest_slurm/logs/'

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

def submit(hpair,q,joblist,dirlist,jobid):
    qopt = ' -p '+q
    d = datetime.datetime.now().strftime('%m_%d_%H%M%S')
    logname = hpair[0]+'_'+hpair[1]+'_'+d+'.log'
    print('launched',logname)
    logopt = ' -o '+logdir+logname
    if hpair[0]==hpair[1]:
        print('*** running single host job')
        hostopt = ' -w '+hpair[0]
    else:
        hostopt = ' -w '+hpair[0]+','+hpair[1]
    timelimit = ' -t %d '%timeLimitMinutes
    pycmd = 'python /reg/g/psdm/utils/batchtest_slurm/batchtest_mpi.py -d '+' '.join(dirlist)
    # openmpi's ORTE requires jobid which doesn't get set when using --no-alloc
    # need to run as user "slurm" to get access to --no-alloc option
    # this in turn requires passwordless sudo for the srun command
    # via /etc/sudoers.d/srun file with a line like this:
    # cpo ALL=(slurm) NOPASSWD:SETENV: /usr/bin/srun
    os.environ['SLURM_JOBID']=str(jobid)
    cmd = 'sudo --preserve-env=PATH,SLURM_JOBID,SIT_DATA -u slurm /usr/bin/srun --no-alloc --jobid='+str(jobid)+timelimit+qopt+logopt+hostopt+' '+pycmd
    subprocess.Popen(cmd, shell=True)
    time.sleep(.1) # this sleep may help srun's that don't seem to start?
    joblist.append(logname)

def submit_all():
    joblist = []
    pairs = []
    nresults = []
    if len(sys.argv)==3:
        forceHostPair = sys.argv[1:]
    else:
        forceHostPair = None
    
    for q,d in zip(queues,dirs):
        openhosts,otherhosts = gethosts(q)
        hoststouse = openhosts
        if forceHostPair is not None:
            # check to see if we've found the right queue
            if forceHostPair[0] in openhosts or forceHostPair[0] in otherhosts:
                if forceHostPair[1] in openhosts or forceHostPair[1] in otherhosts:
                    hoststouse=forceHostPair # override with two selected nodes
                else:
                    raise ValueError('Illegal host pair: %s %s'%
                                     (forceHostPair[0],forceHostPair[1]))
            else:
                # host not in this queue
                continue
        # add the first host back on the end of the array
        if len(hoststouse)>2: hoststouse.append(hoststouse[0])
        for i in range(0,len(hoststouse)-1):
            pairs.append([hoststouse[i],hoststouse[i+1]])
            nresults.append(len(d))
            submit(pairs[-1],q,joblist,d,i+1)
            #time.sleep(5)
    
    if forceHostPair is not None:
        # don't do any automated checking or email messages if we're
        # just running on one pair
        sys.exit()
    
    time.sleep((timeLimitMinutes+headroomMinutes)*60)
    resultString = 'sum: 2268182507.0'
    msg = '\nRan %d jobs\n\n' % len(joblist)
    nerror = 0
    for j,p,numExpected in zip(joblist,pairs,nresults):
        fname = logdir+j
        try:
            f = open(fname)
            contents = f.read()
            f.close()
            numResults = contents.count(resultString)
            if numResults==numExpected:
                os.remove(fname)
            else:
                f.close()
                msg += 'Error: Found %d results, expected %d for job %s on nodes %s,%s\n' % (numResults,numExpected,j,p[0],p[1])
                nerror+=1
        except IOError:
            nerror+=1
            msg += 'Error: No logfile found for job %s on nodes %s,%s\n' % (j,p[0],p[1]
    )
    msg += '\nLogfiles can be found in '+logdir
    from email.mime.text import MIMEText
    from subprocess import Popen, PIPE
    
    mailmsg = MIMEText(msg)
    mailmsg["From"] = "cpo@slac.stanford.edu"
    import getpass
    mailmsg["To"] = getpass.getuser()+"@slac.stanford.edu"
    #if nerror>0:
    #    mailmsg["To"]+=",pcds-it-l@slac.stanford.edu,yoon82"
    mailmsg["Subject"] = "psana batch test"
    p = Popen(["/usr/sbin/sendmail", "-t"], stdin=PIPE)
    p.communicate(mailmsg.as_string())

def checkdirs():
    for d in all_ana:
        subprocess.Popen(['ls','-rtl',d+'/e307-r0999-s00-c00.xtc'])
        subprocess.Popen(['ls','-rtl',d+'/index/e307-r0999-s00-c00.xtc.idx'])

def checkffbdirs():
    for d in calib_ana+ffb:
        subprocess.Popen(['ls','-rtl',d+'/e307-r0999-s00-c00.xtc'])
        subprocess.Popen(['ls','-rtl',d+'/index/e307-r0999-s00-c00.xtc.idx'])

if len(sys.argv)>1 and sys.argv[1]=='checkdirs':
    checkdirs()
elif len(sys.argv)>1 and sys.argv[1]=='checkffbdirs':
    checkffbdirs()
else:
    submit_all()
