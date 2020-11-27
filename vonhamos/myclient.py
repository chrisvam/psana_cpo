from psana import *
import numpy as np
from mpidata import mpidata 

# user parameters
threshold=60 # for thresholding the image
updaterate=10 # how often we push to master, in events
myaxis=1 # for projection direction (either 0 or 1)
myslice = np.s_[10:480,20:70] # roi. full camera is 704*768


def runclient(args):
    setOption('psana.calib-dir','/reg/d/psdm/xcs/xcslv6018/calib')
    ds = DataSource(args.exprun)
    det1 = Detector(args.areaDetName)
    evr = Detector('evr0')

    for run in ds.runs():
        roisum = None
        for nevent,evt in enumerate(run.events()):
            #if nevent >= args.noe : continue # continue since need all the events for multirun analysis: use smd
            img = det1.calib(evt)
            codes = evr.eventCodes(evt)
            if img is None or codes is None: continue
            if 162 in codes or 137 not in codes: continue # only events with beam in xcs
            roi = np.copy(img[myslice]) # copy since data is readonly
            roi[roi<threshold]=0
            if roisum is None:
                proj = np.sum(roi,axis=myaxis)
                if 88 in codes: # las on
                    spectrumsum = np.vstack((proj,np.zeros_like(proj)))
                    nevents_on_off = np.array((1,0))
                else: # las off
                    spectrumsum = np.vstack((np.zeros_like(proj),proj))
                    nevents_on_off = np.array((0,1))
                roisum = roi
                neventsInBatch=1
            else:
                if 88 in codes: # las on
                    spectrumsum[0,:] += np.sum(roi,axis=myaxis)
                    nevents_on_off[0]+=1
                else: # las off
                    spectrumsum[1,:] += np.sum(roi,axis=myaxis)
                    nevents_on_off[1]+=1
                roisum += roi
                neventsInBatch+=1
            if ((nevent)%updaterate == 0): # send mpi data object to master when desired
                senddata=mpidata()
                senddata.addarray('spectrumsum',spectrumsum)
                senddata.addarray('roisum',roisum)
                senddata.addarray('nevents_on_off',nevents_on_off)
                senddata.small.nevents = neventsInBatch
                senddata.send()
                roisum = None # start again
        md = mpidata()
        md.endrun()	
