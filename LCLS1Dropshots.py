from __future__ import print_function
from psana import *
import numpy as np
import sys
from IPython import embed
from matplotlib.backends.backend_pdf import PdfPages
import argparse
parser=argparse.ArgumentParser()
import matplotlib.pyplot as mp
from collections import deque
parser.add_argument("exprun", help="Stick experiment value here. like exp=xpptut15:run=320")
parser.add_argument("--pdf", help="Set to true if you want a series of graphs showing the means. Graphs are stored in the same directory this program is in, with the detector as the name.", action='store_true')
parser.add_argument("--email", help="Enter --email in order to get a useless email", action='store_true')
args=parser.parse_args()
expstring=str(args.exprun)
window=5

class LCLS1_chi_group:

    def __init__(self, window): #Put variables here
        self.detslots={}
        self.msg="The PDFs are found in " + "/cpo/cporo"
        self.mean={}
        self.standdev={} #A bunch of empty dictionaries. Keywords are the detectors.
        self.meanerr={}
        self.maxdropshotcount=10
        self.window=window
        self.eventtime=deque("", window)
        self.eventcode=deque("", window)
        self.supported_dets = ['Epix10ka2M','Wave8','Epix100a','Opal1000','pnCCD','Cspad','EBeam', 'FEEGasDetEnergy', 'PhaseCavity','Jungfrau']
        self.wildcard_dets = ['Pim', 'Ipm', 'BMMON']
        self.bigeventtimelist=[] #Used to store a bunch of event times

    def timestampgatherer(self):
        ds = DataSource(expstring+':smd') #Sets mode to small data mode, apparently because it's easier to scroll through
        evr = Detector('evr0') #evr0 indicates lack of detector. The detector is for later.
        for nevent,evt in enumerate(ds.events()):
            evtid=evt.get(EventId) #...we get an event ID.
            if self.eventcode is None:
                continue
            seconds=int(evtid.time()[0])
            nanoseconds=evtid.time()[1] #Those event IDs get translated into timestamps for storage.
            fiducials=evtid.fiducials()
            self.eventcode.append(evr.eventCodes(evt))
            self.eventtime.append(EventTime(int((seconds<<32)|nanoseconds), fiducials))
            if len(self.eventcode)<self.window:
                continue
            if 162 in self.eventcode[(window//2)]: #162 is the event code for a dropped shot. So if the middle of the dequeue is a dropped shot, it sticks the information in the dequeue into a list.
                self.bigeventtimelist.append(list(self.eventtime))
                continue
            if len(self.bigeventtimelist)==self.maxdropshotcount:
                print('Reached max drop shot count:',self.maxdropshotcount)
                break

    def detresultgetter(self):
        ds=DataSource(expstring+':idx') #Switches the idx mode. More data or somethin'
        good_det_name=self.good_detectors() #Run the good_detectors function near the top. Returns a list.
        print('Supported detectors:',good_det_name) #Just a personal thing, where it spits out a list of detectors it's gonna go through.
        self.detlist=[Detector(detname) for detname in good_det_name]
        run = next(ds.runs())
        for det in self.detlist:
            self.detslots[det.name]=[] #For every detector, it puts in a detector keyword with empty list "detname":[]
            for i in range(window):
                self.detslots[det.name].append([]) #Yoooooo, we got lists... IN LISTS. Perfect for slots
        #print(bigeventtimelist)
        for ndropshots, times in enumerate(self.bigeventtimelist): #Remember that bigeventtimelist are nested lists [[]]
            for islot,t  in enumerate(times): #Second layer of list
                event=run.event(t)
                if event==None:
                    print("None")
                    ipy.embed()
                    print('empty event')
                self.detresult(event, self.detlist, islot) #See function with corresponding name
        run.end()

    def calculations(self):
        for det in self.detlist:
            for nstuff, stuff in enumerate(self.detslots[det.name]):
                self.detslots[det.name][nstuff]=np.array(self.detslots[det.name][nstuff]) #Converts the nasty stuff into arrays for easy calculations

            self.mean[det.name]=[]
            self.standdev[det.name]=[]
            self.meanerr[det.name]=[]
            for n, slot in enumerate(self.detslots[det.name]): #Gettin' all the stuff for the chisquare calculations.
                self.mean[det.name].append(np.mean(slot))
                self.standdev[det.name].append(np.std(slot))
                self.meanerr[det.name].append(np.std(slot)/(len(slot)**.5))

    def detresult(self, event, detlist, islot): #Detresults translates the events into workable arrays and numbers
        for det in detlist:
            if "pnCCD" == det.name.dev or "Cspad" == det.name.dev or "Epix10ka2M"==det.name.dev or "Epix100a"==det.name.dev or "Jungfrau"==det.name.dev or "Opal1000"==det.name.dev:
                calib=det.calib(event)
                if calib is None:
                    continue
                result=np.sum(calib)
            elif "EBeam" == det.name.dev:
                ebeam=det.get(event)
                if ebeam is None:
                    continue
                result=ebeam.ebeamCharge()
            elif "FEEGasDetEnergy" == det.name.dev:
                feeg=det.get(event)
                if feeg is None:
                    continue
                result=feeg.f_11_ENRC()
            elif "PhaseCavity" == det.name.dev:
                phase=det.get(event)
                if phase is None:
                    continue
                result=phase.charge1()
            elif "BMMON" in det.name.dev:
                bmmon=det.get(event)
                if bmmon is None:
                    continue
                result=bmmon.TotalIntensity()
            elif "Ipm" in det.name.dev or "Pim" in det.name.dev:
                val=det.channel(event)
                if val is None:
                    continue
                result=np.sum(val)
            elif "Wave8" in det.name.dev:
                wave=det.raw(event)
                if wave is None:
                    continue
                wavesum=wave[0].astype(float)
                for i in range(1,8):
                    wavesum+=wave[i]
                result=np.sum(wavesum)
            else:
                print('Did not find detector:',det.name)
                continue
            self.detslots[det.name][islot].append(result)
            #print(self.detslots)
    def good_detectors(self):
        good_det=[]
        detnamelist=DetNames("detectors")
        for detname in detnamelist:
            for supported_det in self.supported_dets:
                if supported_det in detname[0]:
                    good_det.append(detname[0])
            for wildcard in self.wildcard_dets:
                if wildcard in detname[0]:
                    good_det.append(detname[0])
        return good_det

dropshotinfo=LCLS1_chi_group(window)
dropshotinfo.timestampgatherer()
ndrop = len(dropshotinfo.bigeventtimelist)
if ndrop>5:
    print('Found',ndrop,'dropped shots.')
else:
    print('Too few dropped shots:',ndrop)
    sys.exit(-1)
dropshotinfo.detresultgetter()
from dropshotcalculations import calculations
emailarg=args.email
pdfarg=args.pdf
calculationvar=calculations(dropshotinfo.detslots, window, emailarg, pdfarg)
calculationvar.calculations()
if args.pdf==True:
    calculationvar.graph(expstring)
calculationvar.chideterminer()
if args.email==True:
    calculationvar.mailer()
