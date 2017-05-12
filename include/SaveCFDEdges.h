#ifndef CPO_SAVECFDEDGES_H
#define CPO_SAVECFDEDGES_H

//--------------------------------------------------------------------------
// File and Version Information:
// 	$Id$
//
// Description:
//	Class SaveCFDEdges.
//
//------------------------------------------------------------------------

//-----------------
// C/C++ Headers --
//-----------------

//----------------------
// Base Class Headers --
//----------------------
#include "psana/Module.h"
#include <fstream>

//-------------------------------
// Collaborating Class Headers --
//-------------------------------

//------------------------------------
// Collaborating Class Declarations --
//------------------------------------

//		---------------------
// 		-- Class Interface --
//		---------------------

namespace cpo {

/// @addtogroup cpo

/**
 *  @ingroup cpo
 *
 *  @brief Example module class for psana
 *
 *  @note This software was developed for the LCLS project.  If you use all or 
 *  part of it, please give an appropriate acknowledgment.
 *
 *  @version \$Id$
 *
 *  @author Christopher Ogrady
 */

class SaveCFDEdges : public Module {
public:

  // Default constructor
  SaveCFDEdges (const std::string& name) ;

  // Destructor
  virtual ~SaveCFDEdges () ;

  /// Method which is called once at the beginning of the job
  virtual void beginJob(Event& evt, Env& env);
  
  /// Method which is called at the beginning of the run
  virtual void beginRun(Event& evt, Env& env);
  
  /// Method which is called at the beginning of the calibration cycle
  virtual void beginCalibCycle(Event& evt, Env& env);
  
  /// Method which is called with event data, this is the only required 
  /// method, all other methods are optional
  virtual void event(Event& evt, Env& env);
  
  /// Method which is called at the end of the calibration cycle
  virtual void endCalibCycle(Event& evt, Env& env);

  /// Method which is called at the end of the run
  virtual void endRun(Event& evt, Env& env);

  /// Method which is called once at the end of the job
  virtual void endJob(Event& evt, Env& env);

protected:

private:

  // Data members, this is for example purposes only
  
  /// Source address of the data object
  Pds::Src        m_src;

  /// String with source name
  Source          m_str_src;
  Source          m_gasdetSrc;

  /// String with key for input data
  std::string     m_key_edges;
  std::string     m_fname_edges_prefix;

  double          m_roi_starttime;
  double          m_roi_endtime;
  unsigned        m_print_edge_pad;

  std::ofstream   _outfile;
  unsigned _evtcount;

};

} // namespace cpo

#endif // CPO_SAVECFDEDGES_H
