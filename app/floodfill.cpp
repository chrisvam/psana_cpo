#include "ndarray/ndarray.h"
#include <stdint.h>
#include <stdio.h>
#include <vector>
#include <fcntl.h>

class Point {
public:
  Point(unsigned r, unsigned c) {
    _val = (r<<16)|c;
  }
  unsigned r() {return _val>>16 & 0xffff;}
  unsigned c() {return _val & 0xffff;}
private:
  unsigned _val;
};

class BlackHole {
public:
  typedef int32_t conmap_t;
  typedef int16_t data_t;
  BlackHole(unsigned nrows,  unsigned ncols, data_t thresh,
            unsigned holeNpixMin, unsigned holeNpixMax) :
    _thresh(thresh), _holeNpixMin(holeNpixMin), _holeNpixMax(holeNpixMax)
  {
    // the "connected map"
    _conmap = make_ndarray<conmap_t>(nrows, ncols);
    _stack.reserve(185*388*2);
  }
  bool floodFill(const ndarray<data_t, 3>& data);
  bool floodFill_recursive(const ndarray<int16_t, 3>& data);
  const ndarray<conmap_t, 2>& conmap() {return _conmap;}
  unsigned numreg() {return _numreg;}
  unsigned lasttrip_seg() {return _lasttrip_seg;}
  unsigned lasttrip_pixcount() {return _lasttrip_pixcount;}

private:
  static const int MAXREGION = 50;
  unsigned _count[MAXREGION];
  bool _edge[MAXREGION];

  void _findConnectedPixels(unsigned seg, unsigned r, unsigned c,
                            const ndarray<data_t, 3>& data);
  bool _maybePush(unsigned seg, unsigned r, unsigned c,
                  const ndarray<int16_t, 3>& data);
  bool _trip();
  ndarray<conmap_t, 2> _conmap;
  unsigned _numreg;
  data_t _thresh;
  unsigned _holeNpixMin;
  unsigned _holeNpixMax;
  unsigned _lasttrip_seg;
  unsigned _lasttrip_pixcount;
  std::vector<Point> _stack;
  };

bool BlackHole::_maybePush(unsigned seg, unsigned r, unsigned c,
                           const ndarray<int16_t, 3>& data) {
  // check for unassigned pixel
  if (_conmap[r][c]==-1) {
    if (data[seg][r][c]>_thresh) {
      _conmap[r][c]=0; // above threshold
    }
    else {
      _stack.push_back(Point(r,c)); // connected pixel
      return true;
    }
  }
  return false;
}

bool BlackHole::floodFill(const ndarray<int16_t, 3>& data) {
  for(unsigned seg = 0; seg<data.shape()[0]; seg++) {
    _numreg=0;
    std::fill_n(_conmap.data(), int(_conmap.size()), conmap_t(-1));
    unsigned nrows = data.shape()[1];
    unsigned ncols = data.shape()[2];
    for(unsigned row = 0; row<nrows; row++) {
      for(unsigned col = 0; col<ncols; col++) {

        if (_maybePush(seg,row,col,data)) {
          ++ _numreg; // start a new region
        } else {
          continue;
        }
        while (!_stack.empty()) {
          Point val = _stack.back();
          _stack.pop_back();
          unsigned r = val.r();
          unsigned c = val.c();
          _conmap[r][c] = _numreg;

          if (r>0)       _maybePush(seg,r-1,c,data);
          if (r<nrows-1) _maybePush(seg,r+1,c,data);
          if (c>0)       _maybePush(seg,r,c-1,data);
          if (c<ncols-1) _maybePush(seg,r,c+1,data);
        }
      }
    }
    bool trip = _trip();
    if (trip) {
      _lasttrip_seg = seg;
      return true;
    }
  }
  return false;
}

bool BlackHole::floodFill_recursive(const ndarray<int16_t, 3>& data) {
  for(unsigned seg = 0; seg<data.shape()[0]; seg++) {
    _numreg=0;
    std::fill_n(_conmap.data(), int(_conmap.size()), conmap_t(-1));
    for(unsigned r = 0; r<data.shape()[1]; r++) {
      for(unsigned c = 0; c<data.shape()[2]; c++) {

        if(data[seg][r][c]>_thresh) {
          _conmap[r][c]=0; // mark as above-threshold
          continue; // don't flood-fill above-threshold regions
        }
        if(_conmap[r][c]>-1) continue; // pixel already assigned to region

        ++ _numreg; // start a new region

        _findConnectedPixels(seg, r, c, data);
      }
    }
    bool trip = _trip();
    if (trip) {
      _lasttrip_seg = seg;
      return true;
    }
  }
  return false;
}

void BlackHole::_findConnectedPixels(unsigned seg, unsigned r, unsigned c,
                                     const ndarray<data_t, 3>& data)
{
  if (data[seg][r][c] > _thresh) return;
  if (_conmap[r][c] > -1) return; // pixel already in region

  _conmap[r][c] = _numreg;

  if( r+1 < data.shape()[1] ) _findConnectedPixels(seg, r+1, c, data);
  if( c+1 < data.shape()[2] ) _findConnectedPixels(seg, r, c+1, data);
  if( r > 0                 ) _findConnectedPixels(seg, r-1, c, data);
  if( c > 0                 ) _findConnectedPixels(seg, r, c-1, data);  
}

bool BlackHole::_trip() {
  std::fill_n(_count, MAXREGION, unsigned(0));
  std::fill_n(_edge, MAXREGION, bool(0));

  for(unsigned r = 0; r<_conmap.shape()[0]; r++) {
    for(unsigned c = 0; c<_conmap.shape()[1]; c++) {
      conmap_t region = _conmap[r][c];
      if (_conmap[r][c]==0) continue;
      if (region==0) continue; // ignore above-threshold pixels
      region -= 1; // to count from zero
      if (region >= MAXREGION) continue; // shouldn't happen
      _count[region]++;
      // ignore any region that has an edge in it (i.e. not
      // completely enclosed)
      if (!_edge[region]) {
        _edge[region] = (r==0) || (r==_conmap.shape()[0]-1) ||
          (c==0) || (c==_conmap.shape()[1]-1);
      }
    }
  }

  for (unsigned i=0; i<_numreg; i++) {
    // trip if we have correct-number of below-threshold pixels
    // not at an edge (we could imagine removing the edge requirement)
    if (_count[i]>=_holeNpixMin && _count[i]<=_holeNpixMax && !_edge[i]) {
      _lasttrip_pixcount = _count[i];
      return true;
    }
  }
  return false;
}

void simpleExample() {
  ndarray<BlackHole::data_t, 3> data = make_ndarray<BlackHole::data_t>(1,3,5);
  std::fill_n(data.data(), int(data.size()), BlackHole::data_t(3));
  data[0][0][1] = 13000;
  data[0][1][0] = 13000;
  data[0][1][1] = 13000;
  data[0][2][3] = 13000;
  data[0][1][3] = 13000;
  data[0][1][4] = 13000;
  for (unsigned i=0; i<data.shape()[1]; i++) {
    for (unsigned j=0; j<data.shape()[2]; j++) {
      printf("%5.5d ",data[0][i][j]);
    }
    printf("\n");
  }
  BlackHole bh = BlackHole(data.shape()[1],data.shape()[2],12000,8,50);
  bh.floodFill(data);
  const ndarray<BlackHole::conmap_t, 2>& cm = bh.conmap();
  for (unsigned i=0; i<cm.shape()[0]; i++) {
    for (unsigned j=0; j<cm.shape()[1]; j++) {
      printf("%d ",cm[i][j]);
    }
    printf("\n");
  }
}

void edge_nohole() {
  // this file is in the "cpo" svn user repo in the "app" dir 
  int f = open("no_blackhole_edge.dat",O_RDONLY);
  if (f==-1) printf("**** failed to open no_blackhole_edge.dat\n");
  ndarray<BlackHole::data_t, 3> data = make_ndarray<BlackHole::data_t>(32,185,388);
  std::fill_n(data.data(), int(data.size()), BlackHole::data_t(-1));
  read(f, data.data(), 8*185*388*sizeof(BlackHole::data_t));
  BlackHole bh = BlackHole(data.shape()[1],data.shape()[2],
                           12000,8,200);
  bool trip = bh.floodFill(data);
  if (trip) printf("blackhole seg %d pixcount %d\n",bh.lasttrip_seg(),bh.lasttrip_pixcount());
}

void real() {
  // this file is in the "cpo" svn user repo in the "app" dir 
  FILE* f = fopen("blackhole.txt","r");
  ndarray<BlackHole::data_t, 3> data = make_ndarray<BlackHole::data_t>(32,185,388);
  BlackHole::data_t tmp;
  for (unsigned i=0; i<32; i++) {
    for (unsigned j=0; j<data.shape()[1]; j++) {
      for (unsigned k=0; k<data.shape()[2]; k++) {
        fscanf(f,"%hd",&tmp);
        data[i][j][k] = tmp;
      }
    }
  }
  BlackHole bh = BlackHole(data.shape()[1],data.shape()[2],
                           12000,8,200);
  bool trip = bh.floodFill(data);
  if (trip) printf("blackhole seg %d pixcount %d\n",bh.lasttrip_seg(),bh.lasttrip_pixcount());
}

int main() {
  //simpleExample();
  printf("This call should find a blackhole\n");
  real();
  printf("This call should not find a blackhole (surrounded edge)\n");
  edge_nohole();
  return 0;
}
