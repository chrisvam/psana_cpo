from psana import *
import subprocess

result = subprocess.check_output(['epix10ka_id exp=mfxc00318:run=13 epix10k2M'], shell=True, stderr=subprocess.STDOUT)
result = result.decode()
ids = ''
for line in result.split('\n'):
   if line.startswith('elem'):
      panel = 'id'+(line.split()[1][:-1]) # remove the last colon
      if ids != '':
         ids+='_'
      ids += line.split()[2]
print(ids)

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

smldata.save(ids=ids)
