from psmon import publish
from psmon.plots import XYPlot,Image
import numpy as np
import collections
import time
from mpidata import mpidata 

publish.plot_opts.aspect = 1

# user parameters
updaterate = 10 # plot-push frequency, measured in "client updates"
deque_len = 30 # how many client updates to use for "recent spectrum"

def runmaster(nClients):
    while (1):
        print('**** New Run ****')
        nClientsInRun = nClients
        myplotter = Plotter()
        while nClientsInRun > 0:
            md = mpidata()
            md.recv()
            if md.small.endrun:
                nClientsInRun -= 1
            else:
                myplotter.update(md)

class Plotter:
    def __init__(self):
        self.nupdate=0
        self.spectrumsum = None
        self.deque = collections.deque(maxlen=deque_len)
        self.lasttime = None
    def update(self,md):
        self.nupdate+=1
    
        if self.spectrumsum is None:
            self.spectrumsum = md.spectrumsum
            self.roisum = md.roisum
            self.nevents = md.small.nevents
            self.nevents_on_off = md.nevents_on_off
        else:
            self.spectrumsum += md.spectrumsum
            self.roisum += md.roisum
            self.nevents += md.small.nevents
            self.nevents_on_off += md.nevents_on_off
        self.avgroisum = self.roisum/self.nevents
        self.deque.append(md.spectrumsum[0,:]+md.spectrumsum[1,:]) # lasing on and off
        if self.nupdate%updaterate==0:
            print('Client updates',self.nupdate,'Master received events:',self.nevents)
            if self.lasttime is not None:
                print('Rate:',(self.nevents-self.lastnevents)/(time.time()-self.lasttime))
            self.lasttime = time.time()
            self.lastnevents = self.nevents
            spectrum_recent = None
            for entry in self.deque:
                if spectrum_recent is None:
                    spectrum_recent=entry
                else:
                    spectrum_recent+=entry
    
            spectrum_on_plot = XYPlot(self.nupdate,"Spectrum On",np.arange(md.spectrumsum.shape[1]),self.spectrumsum[0,:])
            publish.send('SPECTRUM_ON',spectrum_on_plot)
            spectrum_off_plot = XYPlot(self.nupdate,"Spectrum Off",np.arange(md.spectrumsum.shape[1]),self.spectrumsum[1,:])
            publish.send('SPECTRUM_OFF',spectrum_off_plot)
            spectrum_diff_plot = XYPlot(self.nupdate,"Spectrum Diff",np.arange(md.spectrumsum.shape[1]),self.spectrumsum[0,:]*self.nevents_on_off[1]-self.spectrumsum[1,:]*self.nevents_on_off[0])
            publish.send('SPECTRUM_DIFF',spectrum_diff_plot)
            spectrum_recent_plot = XYPlot(self.nupdate,"Recent Spectrum",np.arange(md.spectrumsum.shape[1]),spectrum_recent)
            publish.send('RECENT_SPECTRUM',spectrum_recent_plot)
            roi_plot = Image(self.nupdate,"Epix ROI",self.avgroisum)
            publish.send('EPIX_ROI',roi_plot)
