//--------------------------------------------------------------------------
// File and Version Information:
// 	$Id$
//
// Description:
//	Class SaveCFDEdges...
//
// Author List:
//      Christopher O'Grady
//
//------------------------------------------------------------------------

//-----------------------
// This Class's Header --
//-----------------------
#include "cpo/SaveCFDEdges.h"
#include "psddl_psana/bld.ddl.h"

//-----------------
// C/C++ Headers --
//-----------------

//-------------------------------
// Collaborating Class Headers --
//-------------------------------
#include "MsgLogger/MsgLogger.h"
#include <sstream>

//-----------------------------------------------------------------------
// Local Macros, Typedefs, Structures, Unions and Forward Declarations --
//-----------------------------------------------------------------------

// This declares this class as psana module
using namespace cpo;
PSANA_MODULE_FACTORY(SaveCFDEdges)

//		----------------------------------------
// 		-- Public Function Member Definitions --
//		----------------------------------------

namespace cpo {

//----------------
// Constructors --
//----------------
SaveCFDEdges::SaveCFDEdges (const std::string& name)
  : Module(name)
  , m_src()
  , m_str_src()
  , m_gasdetSrc()
  , m_key_edges()
  , m_fname_edges_prefix()
  , _evtcount(0)
{
  m_str_src            = configSrc("source", "DetInfo(:Acqiris)");
  m_key_edges          = configStr("key_edges", "acqiris_edges_");
  m_fname_edges_prefix = configStr("fname_edges_prefix", "acqiris_edges");
  m_gasdetSrc          = configStr("FEEGasDetEnergySource", "BldInfo(FEEGasDetEnergy)");
  m_roi_starttime      = config   ("roi_starttime", 0.0 );
  m_roi_endtime        = config   ("roi_endtime", 1.0e32 );
  m_print_edge_pad     = config   ("print_edge_pad", 0 );

  _outfile.open((m_fname_edges_prefix+".txt").c_str(),std::ios::trunc);
  _outfile << "% Shot_number GasDet1 GasDet2 GasDet3 GasDet4 AcqChannel 5-electron-events\n";
}

//--------------
// Destructor --
//--------------
SaveCFDEdges::~SaveCFDEdges ()
{
}

/// Method which is called once at the beginning of the job
void 
SaveCFDEdges::beginJob(Event& evt, Env& env)
{
}

/// Method which is called at the beginning of the run
void 
SaveCFDEdges::beginRun(Event& evt, Env& env)
{
  _evtcount=0;
}

/// Method which is called at the beginning of the calibration cycle
void 
SaveCFDEdges::beginCalibCycle(Event& evt, Env& env)
{
}

/// Method which is called with event data, this is the only required 
/// method, all other methods are optional
void 
SaveCFDEdges::event(Event& evt, Env& env)
{
  _evtcount++;

  shared_ptr<Psana::Bld::BldDataFEEGasDetEnergy> gasdet = evt.get(m_gasdetSrc);
  Psana::Bld::BldDataFEEGasDetEnergy *gdet = gasdet.get();

  const unsigned AcqMaxChan=20;
  for (unsigned i=0;i<AcqMaxChan;i++) {
    std::stringstream ss; ss<<i;
    shared_ptr< ndarray<double,2> > ptr = evt.get(m_str_src, m_key_edges+ss.str(), &m_src);
    if (ptr.get()) {
      const ndarray<double,2> &edges = *ptr;
      unsigned nedges = edges.shape()[0];
      if (nedges) {
        unsigned nprint=0;
        unsigned iedge;
        for (iedge=0; iedge<nedges; iedge++) {
          if (edges[iedge][0]>m_roi_starttime && edges[iedge][0]<m_roi_endtime) nprint++;
        }
        if (!nprint) continue;
        _outfile << _evtcount << " ";
        if (gdet) {
          _outfile << gdet->f_11_ENRC() << " " << gdet->f_12_ENRC() << " " 
                   << gdet->f_21_ENRC() << " " << gdet->f_22_ENRC() << " " ;
        } else {
          _outfile << -1.0 << " " << -1.0 << " " << -1.0 << " " << -1.0 << " " ;
        }
        _outfile << i << " ";
        for (iedge=0; iedge<nedges; iedge++) {
          if (edges[iedge][0]>m_roi_starttime && edges[iedge][0]<m_roi_endtime) {
            _outfile << edges[iedge][0] << " ";
          }
        }
        while (nprint++<m_print_edge_pad) _outfile << "-1.0 ";
        _outfile << "\n";
      }
    }
  }

}
  
void 
SaveCFDEdges::endCalibCycle(Event& evt, Env& env)
{
}

void 
SaveCFDEdges::endRun(Event& evt, Env& env)
{
}

void 
SaveCFDEdges::endJob(Event& evt, Env& env)
{
  _outfile.close();
}

} // namespace cpo
