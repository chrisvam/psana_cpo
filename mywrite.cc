#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>

static const unsigned size=0x100000;
static uint32_t data[size];

int main() {
    memset(data,0xffffffff,size*sizeof(uint32_t));
    FILE* f = fopen("/reg/data/drpsrcf/temp/cpo/junk.out","wb"); 
    if (!f) {
        printf("failed to open file\n");
        return -1;
    }
    while (1) {
        fwrite(data,size,1,f);
        usleep(10000);
    }
    fclose(f);
}
