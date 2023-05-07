#import eyed3
#from eyed3 import id3
#audiofile = eyed3.load('/Users/cpolocal/Downloads/01-Super-Bridges.mp3')
#print(audiofile.tag.isV2())
#audiofile.tag.title = 'cpo sb'
#audiofile.tag.save()

from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, TCOM, TCON, TDRC, TRCK
import glob
import shutil

import csv
count = 0
metadata = []
md_titles = []
with open('/Users/cpolocal/Desktop/mp3s/Takeout-11/YouTube and YouTube Music/music-uploads/music-uploads-metadata.csv', newline='') as csvfile:
    myreader = csv.reader(csvfile)
    for row in myreader:
        #print(', '.join(row))
        metadata.append(row)
        md_titles.append(row[0])
        count+=1
print('metadata:',count)

dirpath='/Users/cpolocal/Desktop/mp3s/Takeout-%d/YouTube and YouTube Music/music-uploads/'
takeout_dir = range(10,19)
fnames = []
fnames_no_underscore = []
full_fnames = []
import os
maxfilechars=44 # approx max filename len
for td in takeout_dir:
    root_dir=dirpath%td
    myfiles = glob.glob(root_dir+'*.mp3')
    for nf,f in enumerate(myfiles):
        full_fnames.append(f)
        fname=f[len(dirpath):]
        fname = fname[:-4] # remove .mp3
        # truncate for matching
        if len(fname)>maxfilechars: fname=fname[:maxfilechars]
        #fname = fname.replace('_','') # some problems with _
        fnames.append(fname)
        fnames_no_underscore.append(fname.replace('_',''))
print('files:',len(fnames))
"""
nmissing=0
ntitle=0
nartist=0
nalbum=0
full_fnames_no_md = []
fnames_no_md = []
full_fnames_with_md = []
fnames_with_md = []
for n,(full_fname,fname) in enumerate(zip(full_fnames,fnames)):
    #audio = MP3('/Users/cpolocal/Downloads/01-Super-Bridges.mp3')
    #audio = MP3('/Users/cpolocal/Desktop/Cripple Creek Ferry.mp3')
    audio = MP3(full_fname)
    #print(audio.keys())
    summary = ''
    if 'TALB' in audio.keys():
        summary += 'album:'+audio['TALB'].text[0]+', '
        nalbum +=1
        if 'TPE1' in audio.keys():
            summary += 'artist:'+audio['TPE1'].text[0]+', '
            nartist += 1
        if 'TIT2' in audio.keys():
            summary += 'title:'+audio['TIT2'].text[0]+', '
            ntitle += 1
        #print(summary)
        full_fnames_with_md.append(full_fname)
        fnames_with_md.append(fname)
    else:
        nmissing+=1
        full_fnames_no_md.append(full_fname)
        fnames_no_md.append(fname)
    #print(audio)
    #audio["title"] = TIT2(text="cpo-cc")
    #audio.save()
    #if n>10: break
print('missing metadata:',nmissing,'artist',nartist,'album',nalbum,'title',ntitle)
"""

replace_dict = {'&':'_',"'":'_','(1)':'','(2)':'','(3)':'','(4)':'','(5)':'',
                '(6)':'','(7)':'','"':'','/':'_','?':'',':':'_','*':'_'}

ngood = 0
nbad = 0
dbgstring = 'sdfg' # for debugging failed fname/metadata matches

for nf,(t,md) in enumerate(zip(md_titles,metadata)):
    for rep_key,rep_val in replace_dict.items():
        t = t.replace(rep_key,rep_val)
    #t.replace('_','') # some problems with _
    if len(t)>maxfilechars: t=t[:maxfilechars]
    if dbgstring in t:
        print('***',t,'***',[x for x in fnames if dbgstring in x])
    fname_indices = [i for i,x in enumerate(fnames) if x==t]
    if len(fname_indices)==1: ngood+=1
    else:
        # hack: some metadata seems to be off by just underscores
        fname_indices = [i for i,x in enumerate(fnames_no_underscore) if x==t.replace('_','')]
        if len(fname_indices)==1: ngood+=1
        else:
            nbad+=1
            #print('bad:',t,fname_indices)
            continue
    full_fname = full_fnames[fname_indices[0]]
    #print(md,full_fname)
    #shutil.copy(full_fname,'/Users/cpolocal/Desktop/mp3s_test/')
    # Read the ID3 tag or create one if not present
    try: 
        #print("Found ID3 header")
        tags = ID3(full_fname)
        #print(tags)
    except ID3NoHeaderError:
        #print("Adding ID3 header")
        tags = ID3()

    tags["TIT2"] = TIT2(encoding=3, text=md[0])
    tags["TALB"] = TALB(encoding=3, text=md[1])
    tags["TPE2"] = TPE2(encoding=3, text=md[2])
    tags["TPE1"] = TPE1(encoding=3, text=md[2])

    tags.save(full_fname)
    #if nf>3: break
print('good:',ngood,'bad:',nbad)
