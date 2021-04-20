#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>

static const unsigned size=0x410000;
static uint8_t data[size];

int main() {
    FILE* f = fopen("/cds/data/drpsrcf/temp/cpo/junk.out","rb"); 
    uint64_t totbytes = 0;
    uint64_t ngbytes_last = 0;
    while(1) {
        unsigned nbytes = fread(data,1,size,f);
        totbytes+=nbytes;
        for (unsigned i=0; i<nbytes; i++) {
            if (data[i]!=0xff) printf("%d 0x%x\n",i,data[i]);
        }
        uint64_t ngbytes = totbytes/(1024*1024*1024);
        if (ngbytes!=ngbytes_last) {
            printf("GB: %llu\n",ngbytes);
        }
        ngbytes_last = ngbytes;
    }
    fclose(f);
}
