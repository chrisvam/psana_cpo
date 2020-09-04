from psana import *

dsource = MPIDataSource('exp=mfxc00318:run=13:smd')
epix = Detector('epix10k2M')
smldata = dsource.small_data('epix10k2M.h5',gather_interval=1)

for nevt,evt in enumerate(dsource.events()):
   raw = epix.raw(evt)
   if raw is None:
      print(nevt,'None')
      continue
   smldata.event(raw=raw)
   if nevt>4: break

smldata.save()
