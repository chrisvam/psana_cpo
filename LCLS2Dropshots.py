from psana import *
import numpy as np
import sys
from IPython import embed
from matplotlib.backends.backend_pdf import PdfPages
import argparse
parser=argparse.ArgumentParser()
import matplotlib.pyplot as mp
from collections import deque
parser.add_argument("expname", help="Stick experiment. which in this case will be rixx43518")
parser.add_argument("runnumber", type=int, help="The run number for the experiment, like run 34.")
parser.add_argument("--pdf", help="Set to true if you want a series of graphs showing the means. Graphs are stored in the same directory this program is in, with the detector as the name.", action='store_true')
parser.add_argument("--email", help="Enter --email in order to get a useless email", action='store_true')
args=parser.parse_args()
expname=(args.expname)
runnumber=(args.runnumber)
window=5 #Determines how many "slots" there are, or if you're not the one who made this, how many chisquares you'll get.
droppedeventcode=16
bigeventtimelist=[]
def filter_func(event):
    if event.timestamp in bigeventtimelist:
        return True
    else:
        return False
    

class LCLS2_chi_group:

    def __init__(self, window): #Put variables here
        self.detslots={}
        self.msg="The PDFs are found in " + "/cpo/cporo"
        self.mean={}
        self.standdev={} #A bunch of empty dictionaries. Keywords are the detectors.
        self.meanerr={}
        self.dropshotcount=99 #Can't remember what this does precisely. Might be a limiter of sorts.
        self.window=window
        self.eventtime=deque("", window)
        self.eventcode=deque("", window)
        self.supported_dettypes = ['ebeam', 'xgmd', 'gmd', 'opal', 'wave8', 'hsd', 'pv'] #Slap more detectors in here if  you want, but you'll need to add the methods to the detresult function!
        self.bigeventtimelist=[] #Used to store a bunch of event times

    def timestampgatherer(self):
        ds = DataSource(exp=expname, run=runnumber)
        self.myrun=next(ds.runs())
        timer_det=self.myrun.Detector('timing') #Event code gatherer
        for nevent,event in enumerate(self.myrun.events()):
            if nevent>300:
                break
            timestamp=event.timestamp
            if self.eventcode is None:
                print("none")
                continue
            self.eventcode.append(timer_det.raw.eventcodes(event))
            self.eventtime.append(event.timestamp)
            if len(self.eventcode)<self.window:
                continue
            if self.eventcode[window//2][droppedeventcode]==1:
                self.bigeventtimelist.append(list(self.eventtime))
                continue
            #if len(bigeventtimelist)==dropshotcount: defunct limiter
                #break
        for deque in self.bigeventtimelist:
            for eventtime in deque:
                bigeventtimelist.append(eventtime)

    def detresultgetter(self):
        ds=DataSource(exp=expname, run=runnumber, filter=filter_func) #Switches the idx mode. More data or somethin'
        myrun=next(ds.runs())
        good_det_name=self.good_detectors() #Run the good_detectors function near the top. Returns a list of dettypes.
        print(good_det_name, "good det names") #Just a personal thing, where it spits out a list of detectors it's gonna go through.
        self.detlist=[(myrun.Detector(detname)) for detname in good_det_name]
        for det in self.detlist:
            self.detslots[det._det_name]=[] #For every detector, it puts in a detector keyword with empty list "detname":[]
            for slot in range(window):
                self.detslots[det._det_name].append([]) #Yoooooo, we got lists... IN LISTS. Perfect for slots
        for nevent, event in enumerate(myrun.events()):
            islot=nevent%5
            if nevent>300:
                break
            self.detresult(event, self.detlist, islot) #See function with corresponding name

    def detresult(self, event, detlist, islot): #Detresults translates the events into workable arrays and numbers
        result=None
        for det in detlist:
            if "ebeam" == det._dettype:
                ebeam=det.raw.ebeamCharge(event)
                if ebeam is None:
                    continue
                result=ebeam
            elif "hsd" == det._dettype:
                hsdlist=[]
                hsd=det.raw.waveforms(event)
                if hsd is None:
                    continue
                for dict1 in hsd.values():
                    for key,waveform in dict1.items():
                        if key != "times":
                            hsd2=np.sum(waveform)
                            break
                    break
                result=hsd2
            elif "wave8" == det._dettype:
                func=getattr(det.raw, "raw_0")
                wave=np.sum(func(event))
                if wave==None:
                    continue
                result=wave
            elif "opal"== det._dettype:
                rawopal=det.raw.calib(event)
                if rawopal is None:
                    continue
                opal=np.sum(rawopal)
                result=opal
            elif 'pv' == det._dettype: #In case you're reading this, and you're not me, the manta detector doesn't work. The detector is just too unreliable.
                pv=det.raw.value(event)
                if pv is None:
                    continue
                pv2=np.sum(pv)
                result=pv2
            elif 'xgmd' == det._dettype:
                xgmd=det.raw.energy(event)
                if xgmd is None:
                    continue
                result=xgmd
            elif 'gmd' == det._dettype:
                gmd=det.raw.energy(event)
                if gmd is None:
                    continue
                result=gmd
            self.detslots[det._det_name][islot].append(result)
    def good_detectors(self):
        good_det=[]
        detector_infolist=self.myrun.xtcinfo
        for detector in detector_infolist:
            #detector[1] is the detector type
            if detector[1] in self.supported_dettypes:
                good_det.append(item[0])
            #Put detector (key) in good_det list
            #Check with IPython to see detector type of key use "dir(detector name)"
        return good_det

myslotvars=LCLS2_chi_group(window)
myslotvars.timestampgatherer()
myslotvars.detresultgetter()
from dropshotcalculations import calculations
emailarg=args.email
pdfarg=args.pdf
calculationvar=calculations(myslotvars.detslots, window, pdfarg, emailarg)
calculationvar.calculations()
if args.pdf==True:
    calculationvar.graph()
calculationvar.chideterminer()
if args.email==True:
    calculationvar.mailer()
