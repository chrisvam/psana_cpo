from psana import *
import sys

myrun = sys.argv[1]

dsource = MPIDataSource('exp=amoi0314:run='+myrun+':smd')
det = Detector('AmoETOF.0:Acqiris.0')

smldata = dsource.small_data('/reg/d/psdm/xpp/xpptut13/scratch/cpo/amoi0314_run'+myrun+'.h5',gather_interval=100)

partial_run_sum = None
for nevt,evt in enumerate(dsource.events()):
   wfs = det.waveform(evt)
   if wfs is None:
      print 'None'
      continue
   times = det.wftime(evt)
   smldata.event(waveforms=wfs,times=times)
   if nevt==1000: break

smldata.save()
