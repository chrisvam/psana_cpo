from psana import *
import sys

myrun = sys.argv[1]

dsource = MPIDataSource('exp=amoi0314:run='+myrun+':smd')
acq = Detector('AmoETOF.0:Acqiris.0')
opal = Detector('AmoBPS.0:Opal1000.0')

smldata = dsource.small_data('/reg/g/psdm/tutorials/ami2/tmo/amoi0314_run'+myrun+'.h5',gather_interval=20)

partial_run_sum = None
for nevt,evt in enumerate(dsource.events()):
   wfs = acq.waveform(evt)
   img = opal.raw(evt)
   if wfs is None or img is None:
      print 'None'
      continue
   times = acq.wftime(evt)
   smldata.event(waveforms=wfs,times=times,img=img)

smldata.save()
