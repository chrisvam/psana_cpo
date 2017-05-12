#ifndef CPO_DUMPSMALLDATA_H
#define CPO_DUMPSMALLDATA_H

//--------------------------------------------------------------------------
// File and Version Information:
// 	$Id: DumpSmallData.h 4786 2012-11-15 20:18:45Z salnikov@SLAC.STANFORD.EDU $
//
// Description:
//	Class DumpSmallData.
//
//------------------------------------------------------------------------

//-----------------
// C/C++ Headers --
//-----------------
#include <fstream>

//----------------------
// Base Class Headers --
//----------------------
#include "psana/Module.h"

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

/**
 *  @brief Example module class for psana
 *
 *  This software was developed for the LCLS project.  If you use all or 
 *  part of it, please give an appropriate acknowledgment.
 *
 *  @see AdditionalClass
 *
 *  @version $Id: DumpSmallData.h 4786 2012-11-15 20:18:45Z salnikov@SLAC.STANFORD.EDU $
 *
 *  @author Andrei Salnikov
 */

class DumpSmallData : public Module {
public:

  // Default constructor
  DumpSmallData (const std::string& name) ;

  // Destructor
  virtual ~DumpSmallData () ;

  /// Method which is called at the beginning of job
  virtual void beginJob(Event& evt, Env& env);

  /// Method which is called at the beginning of job
  virtual void beginRun(Event& evt, Env& env);

  /// Method which is called with event data
  virtual void event(Event& evt, Env& env);
  
  /// Method which is called at the beginning of job
  virtual void endRun(Event& evt, Env& env);

protected:

private:

  void dumpBldNames(Event& evt, Env& env);
  void dumpEpicsNames(Event& evt, Env& env);
  void dumpBldValues(Event& evt, Env& env);
  void dumpEpicsValues(Event& evt, Env& env);
  void replaceAll(std::string& str, const std::string& from, const std::string& to);

  Source m_ebeamSrc;
  Source m_cavSrc;
  Source m_feeSrc;
  Source m_ipimbSrc;
  Source m_pimSrc;
  Source m_gmdSrc;

  std::ofstream _str;
  bool     _newrun;
};

} // namespace cpo

#endif // CPO_DUMPSMALLDATA_H
