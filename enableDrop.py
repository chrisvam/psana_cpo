import pickle
from epics import caget, caput, cainfo
import time
import datetime
import os

date = time.strftime('%Y_%m')
now  = time.strftime('%Y-%m-%d %H:%M:%S')
logfile = open('log/'+date,'a')

import sys
sys.stderr = logfile
sys.stdout = logfile
print('---------------')

rightnaow=datetime.datetime.now()
filename='stopperstate.pkl'
minvalue=10000
softxrayabtactName  = 'IOC:IN20:EV01:BYKIKS_ABTACT'
softxrayabtprdName  = 'IOC:IN20:EV01:BYKIKS_ABTPRD'
abtactName      = 'IOC:IN20:EV01:BYKIK_ABTACT' #This and below are for hard xray (Everything except TMO and RIX)
abtprdName      = 'IOC:IN20:EV01:BYKIK_ABTPRD'
newlist=[]
softxray=['PPS:NEH1:1:ST3K4OUTSUM', 'STPR:NEH1:2200:ST1K2OUT']
variablelist=['STPR:XRT1:1:S5OUT_MPSC', 'PPS:FEH1:4:S4STPRSUM', 'PPS:FEH1:6:S6STPRSUM', 'STPR:XRT:1:S45IN_MPSC', 'PPS:NEH1:1:S3INSUM', 'PPS:NEH1:1:ST3K4OUTSUM', 'STPR:NEH1:2200:ST1K2OUT']
hutch=['CXI', 'XCS', 'MEC', 'MFX', 'XPP', 'TMO', 'RIX']
openedlist=[1, 0, 0, 1, 0, 1, 1] #These numbers signify the opened state of a stopper

for stopper in variablelist:
    newlist.append(caget(stopper))
if os.path.isfile(filename)==False:
    savinglist=newlist
    print("No file")
    file=open(filename, 'wb')
    pickle.dump(savinglist, file)
    print("Save file created")
    file.close()
    print("saved states: " , savinglist)
    quit()

savedstateprimer=open(filename, 'rb')
savinglist=pickle.load(savedstateprimer)
print("Checked stoppers at: " , rightnaow)
print(savinglist)
savedstateprimer.close()
totallist=zip(variablelist, openedlist, newlist, savinglist, hutch)

for stopper, openstatus, newstate, savedstate, hutches   in totallist:
    print(hutches, "Stopper opens on",  openstatus, "Stopper status is",  newstate, "Stopper status was previously",  savedstate)
    if newstate==openstatus and savedstate!=openstatus:
        print(hutch," opened")
        if stopper in softxray:
            if softxrayabtact.value == 0 or softxrayabtprd.value>minvalue:
                caput(softxrayabtprdName, minvalue)
                caput(softxrayabtactName, 1)
                print("Soft xray drop shot period set to %d at %s"%(minvalue,rightnaow))
        else:
            if abtact.value == 0 or abtprd.value>minvalue:
                caput(abtprdName, minvalue)
                caput(abtactName, 1)
                print("Hard xray drop shot period set to %d at %s"%(minvalue,rightnaow))
newsavedstate=open(filename, 'wb')
savedlist=pickle.dump(newlist, newsavedstate)
newsavedstate.close()
#caget -d DBR_CTRL_ENUM (Stopper name) gets ya the descriptions of the states
#S5OUT_MPSC: 0=closed, 1=open
#S4STPRSUM: 0=open 4=closed
#S6STPRSUM: 0=open 4=closed
#S45IN_NPSC: 0: open, 1=closed
#S3INSUM: 0=open, 1=closed
#ST3K4OUTSUM: 0=closed, 1=open
#ST1K2OUT: 0=closed, 1=open
