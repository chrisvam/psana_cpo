#include <fcntl.h>
#include <map>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <unistd.h>
#include <errno.h>

#include "xtcdata/xtc/XtcFileIterator.hh"
#include "xtcdata/xtc/XtcIterator.hh"
#include "xtcdata/xtc/ShapesData.hh"
#include "xtcdata/xtc/DescData.hh"

using namespace XtcData;
using std::string;

class StreamHeader {
  public:
    StreamHeader() {}
  public:
    unsigned num_samples() const { return _word[0]&0x3fffffff; }
    unsigned stream_id  () const { return (_word[1]>>24)&0xff; }
    unsigned samples () const { return num_samples(); } // number of samples
    bool     unlocked() const { return (_word[0]>>30)&1; }        // data serial link unlocked
    bool     overflow() const { return (_word[0]>>31)&1; }        // overflow of memory buffer
    unsigned strmtype() const { return (_word[1]>>24)&0xff; } // type of stream {raw, thr, ...}
    unsigned boffs   () const { return (_word[1]>>0)&0xff; }  // padding at start
    unsigned eoffs   () const { return (_word[1]>>8)&0xff; }  // padding at end
    unsigned buffer  () const { return _word[1]>>16; }        // 16 front-end buffers (like FEE)
    // (only need 4 bits but using 16)
    unsigned toffs   () const { return (_word[2]>> 0)&0xffff; } // phase between sample clock and timing clock (1.25GHz)
    unsigned l1tag   () const { return (_word[2]>>16)&0x1f; }   // trigger tag word
    // wrong if this value is not fixed
    unsigned baddr   () const { return _word[3]&0xffff; }     // begin address in circular buffer
    unsigned eaddr   () const { return _word[3]>>16; }        // end address in circular buffer
    void     dump    () const
    {
      printf("StreamHeader dump\n");
      printf("  ");
      for(unsigned i=0; i<4; i++)
        printf("%08x%c", _word[i], i<3 ? '.' : '\n');
      printf("  size [%04u]  boffs [%u]  eoffs [%u]  buff [%u]  toffs[%04u]  baddr [%04x]  eaddr [%04x]\n",
             samples(), boffs(), eoffs(), buffer(), toffs(), baddr(), eaddr());
    }
public:
    uint32_t _word[4];
};

class ChannelPython {
public:
    ChannelPython() {}
    ChannelPython(uint32_t *evtheader, uint8_t* data) :
        _evtheader(evtheader), _data(data), _sh_raw(0), _sh_fex(0)
    {
        _reset_peakiter();
        unsigned streams((evtheader[0]>>20)&0x3);
        uint8_t* p = data;
        while(streams) {
            StreamHeader* sh = reinterpret_cast<StreamHeader*>(p);
            if (sh->stream_id() == 0) {
                _sh_raw = sh;
            }
            if (sh->stream_id() == 1) {
                _sh_fex = sh;
            }
            p += sizeof(StreamHeader)+sh->num_samples()*2;
            streams &= ~(1<<sh->stream_id());
        }
    }

    ~ChannelPython(){}

    uint16_t* waveform(unsigned& numsamples) {
        if (!_sh_raw) return 0;
        numsamples = _sh_raw->num_samples();
        uint16_t* wf = (uint16_t*)(_sh_raw+1);
        return wf;
    }

    //  For debugging the processing in this class
    // uint16_t* sparse(unsigned& numsamples) {
    //     if (!_sh_fex) return 0;
    //     numsamples = _sh_fex->num_samples();
    //     uint16_t* wf = (uint16_t*)(_sh_fex+1);
    //     return wf;
    // }

    unsigned next_peak(unsigned& startPos, uint16_t** peakPtr) {
        unsigned peakLen = 0; // indicate that, by default, we haven't found a peak
        if (!_sh_fex) return peakLen; // no more peaks to look for
        uint16_t* q = reinterpret_cast<uint16_t*>(_sh_fex+1);

        unsigned i;
        for(i=_startSample; i<_sh_fex->num_samples();) {
            if (q[i]&0x8000) { // are we a "skip" sample?
                for (unsigned j=0; j<4; j++, i++) {
                    _ns += (q[i]&0x7fff); // increment the number-of-skips
                }
                if (_in) { // if we were previously in a peak, this completes that peak
                    _totWidth += _width; // add the width of the last peak to the cumulative sum
                    peakLen = _width;
                    _startSample = i; // remember where to start for next call
                    _in = false; // we're not in a peak anymore
                    return peakLen;
                }
            } else {
                if (!_in) { // we weren't previously in a peak, so start a new one
                    _width = 0;
                    startPos = _ns+_totWidth; // the index into the raw waveform: number-of-skips plus width of all previous peaks
                    *peakPtr = (uint16_t *) (q+i); // pointer to the start of the peak array
                }
                i += 4; // move to the next (interleaved) sample
                _width += 4; // increment the width of this peak
                _in = true; // we are in a peak
            }
        }
        if (_in) {
            // I think this case happens when the last peak includes
            // the very last uint16_t in sh_fex payload.
            peakLen = _width;
        }
        // these two lines will cause the iterator to return 0
        // on the next call, ending the iteration.
        _startSample = i;
        _in = false;
        return peakLen;
    }
private:
    uint32_t* _evtheader;
    uint8_t*  _data;
public:
    StreamHeader* _sh_raw;
    StreamHeader* _sh_fex;

    void _reset_peakiter() {
        _ns=0;
        _in = false;
        _width = 0;
        _totWidth = 0;
        _startSample = 0;
    }

    unsigned _ns;
    bool     _in;
    unsigned _width;
    unsigned _totWidth;
    unsigned _startSample;

};

template<typename T> static void _dump(const char* name,  Array<T> arrT, unsigned numWords, unsigned* shape, unsigned rank, const char* fmt)
{
    printf("'%s' ", name);
    printf("(shape:");
    for (unsigned w = 0; w < rank; w++) printf(" %d",shape[w]);
    printf("): ");
    for (unsigned w = 0; w < numWords; ++w) {
        printf(fmt, arrT.data()[w]);
    }
    printf("\n");
}

class DebugIter : public XtcIterator
{
public:
    enum { Stop, Continue };
    DebugIter(unsigned numWords) : XtcIterator(), _numWords(numWords)
    {
    }

    void get_value(int i, Name& name, DescData& descdata){
        int data_rank = name.rank();
        int data_type = name.type();
        if (strcmp(name.name(),"eventHeader")==0) {
            _hsdheader = descdata.get_array<uint32_t>(i);
            // fixup the event header to remove the "raw-waveform" bit
            _hsdheader.data()[0]&=0xffefffff;
        }
        if (strcmp(name.name(),"chan00")==0) {
            _hsddata = descdata.get_array<uint8_t>(i);
            ChannelPython chanpy(_hsdheader.data(),_hsddata.data());
            unsigned numsamples=0;
            _sh_raw = chanpy._sh_raw;
            _sh_fex = chanpy._sh_fex;
        }
        return;
            
        switch(name.type()){
        case(Name::UINT8):{
            if(data_rank > 0){
                _dump<uint8_t>(name.name(), descdata.get_array<uint8_t>(i), _numWords, descdata.shape(name), name.rank(), " %d");
            }
            else{
                printf("'%s': %d\n",name.name(),descdata.get_value<uint8_t>(i));
            }
            break;
        }

        case(Name::UINT16):{
            if(data_rank > 0){
                _dump<uint16_t>(name.name(), descdata.get_array<uint16_t>(i), _numWords, descdata.shape(name), name.rank(), " %d");
            }
            else{
                printf("'%s': %d\n",name.name(),descdata.get_value<uint16_t>(i));
            }
            break;
        }

        case(Name::UINT32):{
            if(data_rank > 0){
                _dump<uint32_t>(name.name(), descdata.get_array<uint32_t>(i), _numWords, descdata.shape(name), name.rank(), " %d");
            }
            else{
                printf("'%s': %d\n",name.name(),descdata.get_value<uint32_t>(i));
            }
            break;
        }

        case(Name::UINT64):{
            if(data_rank > 0){
                _dump<uint64_t>(name.name(), descdata.get_array<uint64_t>(i), _numWords, descdata.shape(name), name.rank(), " %ld");
            }
            else{
                printf("'%s': %llu\n",name.name(),descdata.get_value<uint64_t>(i));
            }
            break;
        }

        case(Name::INT8):{
            if(data_rank > 0){
                _dump<int8_t>(name.name(), descdata.get_array<int8_t>(i), _numWords, descdata.shape(name), name.rank(), " %d");
            }
            else{
                printf("'%s': %d\n",name.name(),descdata.get_value<int8_t>(i));
            }
            break;
        }

        case(Name::INT16):{
            if(data_rank > 0){
                _dump<int16_t>(name.name(), descdata.get_array<int16_t>(i), _numWords, descdata.shape(name), name.rank(), " %d");
            }
            else{
                printf("'%s': %d\n",name.name(),descdata.get_value<int16_t>(i));
            }
            break;
        }

        case(Name::INT32):{
            if(data_rank > 0){
                _dump<int32_t>(name.name(), descdata.get_array<int32_t>(i), _numWords, descdata.shape(name), name.rank(), " %d");
            }
            else{
                printf("'%s': %d\n",name.name(),descdata.get_value<int32_t>(i));
            }
            break;
        }

        case(Name::INT64):{
            if(data_rank > 0){
                _dump<int64_t>(name.name(), descdata.get_array<int64_t>(i), _numWords, descdata.shape(name), name.rank(), " %ld");
            }
            else{
                printf("'%s': %lld\n",name.name(),descdata.get_value<int64_t>(i));
            }
            break;
        }

        case(Name::FLOAT):{
            if(data_rank > 0){
                _dump<float>(name.name(), descdata.get_array<float>(i), _numWords, descdata.shape(name), name.rank(), " %f");
            }
            else{
                printf("'%s': %f\n",name.name(),descdata.get_value<float>(i));
            }
            break;
        }

        case(Name::DOUBLE):{
            if(data_rank > 0){
                _dump<double>(name.name(), descdata.get_array<double>(i), _numWords, descdata.shape(name), name.rank(), " %f");
            }
            else{
                printf("'%s': %f\n",name.name(),descdata.get_value<double>(i));
            }
            break;
        }

        case(Name::CHARSTR):{
            if(data_rank > 0){
                Array<char> arrT = descdata.get_array<char>(i);
                printf("'%s': \"%s\"\n",name.name(),arrT.data());
            }
            else{
                printf("'%s': string with no rank?!?\n",name.name());
            }
            break;
        }

        case(Name::ENUMVAL):{
            if(data_rank > 0){
                _dump<int32_t>(name.name(), descdata.get_array<int32_t>(i), _numWords, descdata.shape(name), name.rank(), " %d");
            }
            else{
                printf("'%s': %d\n",name.name(),descdata.get_value<int32_t>(i));
            }
            break;
        }

        case(Name::ENUMDICT):{
            if(data_rank > 0){
                printf("'%s': enumdict with rank?!?\n", name.name());
            } else{
                printf("'%s': %d\n",name.name(),descdata.get_value<int32_t>(i));
            }
            break;
        }
        }
    }

    int process(Xtc* xtc)
    {
        switch (xtc->contains.id()) {
        case (TypeId::Parent): {
            printf("*** parent\n");
            iterate(xtc);
            break;
        }
        case (TypeId::Names): {
            Names& names = *(Names*)xtc;
            _namesLookup[names.namesId()] = NameIndex(names);
            Alg& alg = names.alg();
	    printf("*** DetName: %s, Segment %d, DetType: %s, DetId: %s, Alg: %s, Version: 0x%6.6x, namesid: 0x%x, Names:\n",
                   names.detName(), names.segment(), names.detType(), names.detId(),
                   alg.name(), alg.version(), (int)names.namesId());

            for (unsigned i = 0; i < names.num(); i++) {
                Name& name = names.get(i);
                printf("Name: '%s' Type: %d Rank: %d\n",name.name(),name.type(), name.rank());
            }

            break;
        }
        case (TypeId::ShapesData): {
            ShapesData& shapesdata = *(ShapesData*)xtc;
            _shapesdata = &shapesdata;
            _data = &(shapesdata.data());
            _shapes = &(shapesdata.shapes());
            // lookup the index of the names we are supposed to use
            NamesId namesId = shapesdata.namesId();
            // protect against the fact that this namesid
            // may not have a NamesLookup.  cpo thinks this
            // should be fatal, since it is a sign the xtc is "corrupted",
            // in some sense.
            if (_namesLookup.count(namesId)<=0) {
                printf("*** Corrupt xtc: namesid 0x%x not found in NamesLookup\n",(int)namesId);
                throw "invalid namesid";
                break;
            }
            DescData descdata(shapesdata, _namesLookup[namesId]);
            Names& names = descdata.nameindex().names();
            Data& data = shapesdata.data();
            for (unsigned i = 0; i < names.num(); i++) {
                Name& name = names.get(i);
                get_value(i, name, descdata);
            }
            break;
        }
        default:
            break;
        }
        return Continue;
    }

private:
    NamesLookup _namesLookup;
    unsigned _numWords;
public:
    Array<uint32_t> _hsdheader;
    Array<uint8_t> _hsddata;
    Xtc* _shapesdata;
    Xtc* _data;
    Xtc* _shapes;
    StreamHeader* _sh_raw;
    StreamHeader* _sh_fex;
};


void usage(char* progname)
{
    fprintf(stderr, "Usage: %s -f <filename> [-d] [-n <nEvents>] [-w <nWords>] [-h]\n", progname);
}

int main(int argc, char* argv[])
{
    int c;
    char* xtcname = 0;
    int parseErr = 0;
    unsigned neventreq = 0xffffffff;
    bool debugprint = false;
    unsigned numWords = 3;

    while ((c = getopt(argc, argv, "hf:n:dw:")) != -1) {
        switch (c) {
        case 'h':
            usage(argv[0]);
            exit(0);
        case 'f':
            xtcname = optarg;
            break;
        case 'n':
            neventreq = atoi(optarg);
            break;
        case 'd':
            debugprint = true;
            break;
        case 'w':
            numWords = atoi(optarg);
            break;
        default:
            parseErr++;
        }
    }

    if (!xtcname) {
        usage(argv[0]);
        exit(2);
    }

    int fd = open(xtcname, O_RDONLY);
    FILE* outfile = fopen("test.xtc2", "w");
    if (fd < 0) {
        fprintf(stderr, "Unable to open file '%s'\n", xtcname);
        exit(2);
    }

    XtcFileIterator iter(fd, 0x4000000);
    Dgram* dg;
    unsigned nevent=0;
    DebugIter dbgiter(numWords);
    uint64_t counting_timestamp=0;
    while ((dg = iter.next())) {
        if (dg->service()==TransitionId::SlowUpdate) continue;
        if (nevent>=neventreq) break;
        nevent++;
        dbgiter.iterate(&(dg->xtc));
        dg->time = TimeStamp(counting_timestamp);
        if (dg->service()==TransitionId::L1Accept) {
            // patch up the xtc with only the peak info
            unsigned sizeofwf = (char*)dbgiter._sh_fex-(char*)dbgiter._sh_raw;
            // make sure we remove the event header size from the payload
            // size of the Data xtc payload is hsdevtheader+rawwf+fex where
            // the latter two have an hsdstreamheader
            unsigned sizeofpeaks = dbgiter._data->sizeofPayload()-sizeofwf-dbgiter._hsdheader.shape()[0]*sizeof(uint32_t);
            memcpy(dbgiter._sh_raw,dbgiter._sh_fex,sizeofpeaks);
            dbgiter._shapesdata->extent-=sizeofwf;
            dbgiter._data->extent-=sizeofwf;
            uint32_t* shapes = (uint32_t*)(dbgiter._shapes->payload());
            //printf("shape %d %d %d\n",shapes[0],shapes[5],shapes[10]);
            shapes[5]-=sizeofwf; // hsd array is second one (each shape has 5 entries). first array is hsd eventheader (8 bytes)
            dg->xtc.extent-=sizeofwf;
        }
        if (fwrite(dg, sizeof(*dg) + dg->xtc.sizeofPayload(), 1, outfile) != 1) {
            printf("Error writing to output xtc file.\n",dg->xtc.sizeofPayload());
            perror("main");
        }
        counting_timestamp++;
    }

    ::close(fd);
    return 0;
}
