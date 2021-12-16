import os
import numpy as np
from psana import DataSource
from psmon import publish
from psmon.plots import XYPlot,Image
from collections import deque

from mpi4py import MPI
numworkers = MPI.COMM_WORLD.Get_size()-1
if numworkers==0: numworkers=1 # the single core case (no mpi)

os.environ['PS_SRV_NODES']='1' # one mpi core gathers/plots data

mydeque=deque(maxlen=25)
lastimg=None
numevents=0
numendrun=0

def my_smalldata(data_dict): # one core gathers all data from mpi workers
    global numevents,lastimg,numendrun,mydeque
    if 'endrun' in data_dict:
        numendrun+=1
        if numendrun==numworkers:
            print('Received endrun from all workers. Resetting data.')
            numendrun=0
            numevents=0
            mydeque=deque(maxlen=25)
        return
    numevents += 1
    if 'opal' in data_dict:
        lastimg = data_dict['opal']
    mydeque.append(data_dict['opalsum'])
    if numevents%100==0: # update plots around 1Hz
        print('event:',numevents)
        myxyplot = XYPlot(numevents, "Last 25 Sums", np.arange(len(mydeque)), np.array(mydeque), formats='o')
        publish.send("OPALSUMS", myxyplot)
        if lastimg is not None: # opal image is not sent all the time
            myimgplot = Image(numevents, "Opal Image", lastimg)
            publish.send("OPALIMG", myimgplot)

while 1: # mpi worker processes
    ds = DataSource(shmem='rix')
    smd = ds.smalldata(batch_size=5, callbacks=[my_smalldata])
    for myrun in ds.runs():
        opal = myrun.Detector('atmopal')
        for nevt,evt in enumerate(myrun.events()):
            mydict={}
            image = opal.raw.image(evt)
            if image is None: continue
            # do as much work as possible in the workers
            # don't send large data all the time, if possible
            if nevt%10==0: mydict['opal']=image
            mydict['opalsum']=np.sum(image)
            smd.event(evt,mydict)
        smd.event(evt,{'endrun':1}) # tells gatherer to reset plots
