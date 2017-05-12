//--------------------------------------------------------------------------
// File and Version Information:
// 	$Id: DumpSmallData.cpp 6920 2013-10-07 22:09:39Z salnikov@SLAC.STANFORD.EDU $
//
// Description:
//	Class DumpSmallData...
//
// Author List:
//      Andrei Salnikov
//
//------------------------------------------------------------------------

//-----------------------
// This Class's Header --
//-----------------------
#include "cpo/DumpSmallData.h"

//-----------------
// C/C++ Headers --
//-----------------
#include <iomanip>
#include <string>

//-------------------------------
// Collaborating Class Headers --
//-------------------------------
#include "psddl_psana/bld.ddl.h"
#include "ImgAlgos/GlobalMethods.h"

//-----------------------------------------------------------------------
// Local Macros, Typedefs, Structures, Unions and Forward Declarations --
//-----------------------------------------------------------------------

using namespace cpo;
PSANA_MODULE_FACTORY(DumpSmallData)

//		----------------------------------------
// 		-- Public Function Member Definitions --
//		----------------------------------------

namespace cpo {

//----------------
// Constructors --
//----------------
DumpSmallData::DumpSmallData (const std::string& name)
  : Module(name)
{
  m_ebeamSrc = configSrc("eBeamSource", "BldInfo(EBeam)");
  m_cavSrc = configSrc("phaseCavSource", "BldInfo(PhaseCavity)");
  m_feeSrc = configSrc("feeSource", "BldInfo(FEEGasDetEnergy)");
  m_ipimbSrc = configSrc("ipimbSource", "BldInfo(NH2-SB1-IPM-01)");
  m_pimSrc = configSrc("pimSource", "BldInfo(XCS-DIO-01)");
  m_gmdSrc = configSrc("gmdSource", "BldInfo()");
}

//--------------
// Destructor --
//--------------
DumpSmallData::~DumpSmallData ()
{
}

void
DumpSmallData::beginJob(Event& evt, Env& env)
{
}

void
DumpSmallData::beginRun(Event& evt, Env& env)
{
  std::string fname = "SmallData-r" + ImgAlgos::stringRunNumber(evt) 
    + ".txt";
  _str.open(fname.c_str());
  _newrun=1;

}

void
DumpSmallData::endRun(Event& evt, Env& env)
{
  _str.close();
}

// Method which is called with event data
void 
DumpSmallData::event(Event& evt, Env& env)
{
  _str << std::scientific;
  _str.precision(7);
  _str << std::setw(40);
  if (_newrun) {
    _str << std::setw(40) << "timestamp";
    dumpBldNames(evt,env);
    dumpEpicsNames(evt,env);
    _str<<std::endl;
    _newrun=0;
  }
  _str << std::setw(40) << ImgAlgos::stringTimeStamp(evt) ;
  dumpBldValues(evt,env);
  dumpEpicsValues(evt,env);
  _str<<std::endl;
}

void 
DumpSmallData::dumpBldNames(Event& evt, Env& env)
{
  shared_ptr<Psana::Bld::BldDataEBeamV0> ebeam0 = evt.get(m_ebeamSrc);
  if (ebeam0) {
      _str << std::setw(40) << "ebeamdamageMask"
          << std::setw(40) << "ebeamCharge"
          << std::setw(40) << "ebeamL3Energy"
          << std::setw(40) << "ebeamLTUPosX"
          << std::setw(40) << "ebeamLTUPosY"
          << std::setw(40) << "ebeamLTUAngX"
           << std::setw(40) << "ebeamLTUAngY";
  }

  shared_ptr<Psana::Bld::BldDataEBeamV1> ebeam1 = evt.get(m_ebeamSrc);
  if (ebeam1) {
      _str << std::setw(40) << "ebeamdamageMask"
          << std::setw(40) << "ebeamCharge"
          << std::setw(40) << "ebeamL3Energy"
          << std::setw(40) << "ebeamLTUPosX"
          << std::setw(40) << "ebeamLTUPosY"
          << std::setw(40) << "ebeamLTUAngX"
          << std::setw(40) << "ebeamLTUAngY"
           << std::setw(40) << "ebeamPkCurrBC2";
  }

  shared_ptr<Psana::Bld::BldDataEBeamV2> ebeam2 = evt.get(m_ebeamSrc);
  if (ebeam2) {
      _str << std::setw(40) << "ebeamdamageMask"
          << std::setw(40) << "ebeamCharge"
          << std::setw(40) << "ebeamL3Energy"
          << std::setw(40) << "ebeamLTUPosX"
          << std::setw(40) << "ebeamLTUPosY"
          << std::setw(40) << "ebeamLTUAngX"
          << std::setw(40) << "ebeamLTUAngY"
          << std::setw(40) << "ebeamPkCurrBC2"
           << std::setw(40) << "ebeamEnergyBC2";
  }

  shared_ptr<Psana::Bld::BldDataEBeamV3> ebeam3 = evt.get(m_ebeamSrc);
  if (ebeam3) {
      _str << std::setw(40) << "ebeamdamageMask"
          << std::setw(40) << "ebeamCharge"
          << std::setw(40) << "ebeamL3Energy"
          << std::setw(40) << "ebeamLTUPosX"
          << std::setw(40) << "ebeamLTUPosY"
          << std::setw(40) << "ebeamLTUAngX"
          << std::setw(40) << "ebeamLTUAngY"
          << std::setw(40) << "ebeamPkCurrBC2"
          << std::setw(40) << "ebeamEnergyBC2"
          << std::setw(40) << "ebeamPkCurrBC1"
           << std::setw(40) << "ebeamEnergyBC1";
  }

  shared_ptr<Psana::Bld::BldDataEBeamV4> ebeam4 = evt.get(m_ebeamSrc);
  if (ebeam4) {
      _str << std::setw(40) << "ebeamdamageMask"
          << std::setw(40) << "ebeamCharge"
          << std::setw(40) << "ebeamL3Energy"
          << std::setw(40) << "ebeamLTUPosX"
          << std::setw(40) << "ebeamLTUPosY"
          << std::setw(40) << "ebeamLTUAngX"
          << std::setw(40) << "ebeamLTUAngY"
          << std::setw(40) << "ebeamPkCurrBC2"
          << std::setw(40) << "ebeamEnergyBC2"
          << std::setw(40) << "ebeamPkCurrBC1"
          << std::setw(40) << "ebeamEnergyBC1"
          << std::setw(40) << "ebeamUndPosX"
          << std::setw(40) << "ebeamUndPosY"
          << std::setw(40) << "ebeamUndAngX"
           << std::setw(40) << "ebeamUndAngY";
  }

  shared_ptr<Psana::Bld::BldDataPhaseCavity> cav = evt.get(m_cavSrc);
  if (cav) {
      _str << std::setw(40) << "phaseCavFitTime1"
          << std::setw(40) << "phaseCavFitTime2"
          << std::setw(40) << "phaseCavCharge1"
           << std::setw(40) << "phaseCavcharge2";
  }
  
  shared_ptr<Psana::Bld::BldDataFEEGasDetEnergy> fee = evt.get(m_feeSrc);
  if (fee) {
      _str << std::setw(40) << "GasDet_f_11_ENRC"
          << std::setw(40) << "GasDet_f_12_ENRC"
          << std::setw(40) << "GasDet_f_21_ENRC"
           << std::setw(40) << "GasDet_f_22_ENRC";
  }

  // dump BldDataGMDV0
  shared_ptr<Psana::Bld::BldDataGMDV0> gmd0 = evt.get(m_gmdSrc);
  if (gmd0) {
      _str << std::setw(40) << "gmd_gasType"
          << std::setw(40) << "gmd_pressure"
          << std::setw(40) << "gmd_temperature"
          << std::setw(40) << "gmd_current"
          << std::setw(40) << "gmd_hvMeshElectron"
          << std::setw(40) << "gmd_hvMeshIon"
          << std::setw(40) << "gmd_hvMultIon"
          << std::setw(40) << "gmd_chargeQ"
          << std::setw(40) << "gmd_photonEnergy"
          << std::setw(40) << "gmd_multPulseIntensity"
          << std::setw(40) << "gmd_keithleyPulseIntensity"
          << std::setw(40) << "gmd_pulseEnergy"
          << std::setw(40) << "gmd_pulseEnergyFEE"
          << std::setw(40) << "gmd_transmission"
           << std::setw(40) << "gmd_transmissionFEE";
  }

  // dump BldDataGMDV1
  shared_ptr<Psana::Bld::BldDataGMDV1> gmd1 = evt.get(m_gmdSrc);
  if (gmd1) {
      _str << std::setw(40) << "gmd_milliJoulesPerPulse"
          << std::setw(40) << "gmd_milliJoulesAverage"
          << std::setw(40) << "gmd_correctedSumPerPulse"
          << std::setw(40) << "gmd_bgValuePerSample"
           << std::setw(40) << "gmd_relativeEnergyPerPulse";
  }

  // dump BldDataSpectrometerV0
  shared_ptr<Psana::Bld::BldDataSpectrometerV0> spec0 = evt.get(m_gmdSrc);
  if (spec0) {
      _str << std::setw(40) << "spec_hproj"
           << std::setw(40) << "spec_vproj";
  }

}

void 
DumpSmallData::dumpBldValues(Event& evt, Env& env)
{
  shared_ptr<Psana::Bld::BldDataEBeamV0> ebeam0 = evt.get(m_ebeamSrc);
  if (ebeam0) {
      _str << std::showbase << std::hex << std::setw(40) << ebeam0->damageMask() << std::dec
          << std::setw(40) << ebeam0->ebeamCharge()
          << std::setw(40) << ebeam0->ebeamL3Energy()
          << std::setw(40) << ebeam0->ebeamLTUPosX()
          << std::setw(40) << ebeam0->ebeamLTUPosY()
          << std::setw(40) << ebeam0->ebeamLTUAngX()
           << std::setw(40) << ebeam0->ebeamLTUAngY();
  }

  shared_ptr<Psana::Bld::BldDataEBeamV1> ebeam1 = evt.get(m_ebeamSrc);
  if (ebeam1) {
      _str << std::showbase << std::hex << std::setw(40) << ebeam1->damageMask() << std::dec
          << std::setw(40) << ebeam1->ebeamCharge()
          << std::setw(40) << ebeam1->ebeamL3Energy()
          << std::setw(40) << ebeam1->ebeamLTUPosX()
          << std::setw(40) << ebeam1->ebeamLTUPosY()
          << std::setw(40) << ebeam1->ebeamLTUAngX()
          << std::setw(40) << ebeam1->ebeamLTUAngY()
           << std::setw(40) << ebeam1->ebeamPkCurrBC2();
  }

  shared_ptr<Psana::Bld::BldDataEBeamV2> ebeam2 = evt.get(m_ebeamSrc);
  if (ebeam2) {
      _str << std::showbase << std::hex << std::setw(40) << ebeam2->damageMask() << std::dec
          << std::setw(40) << ebeam2->ebeamCharge()
          << std::setw(40) << ebeam2->ebeamL3Energy()
          << std::setw(40) << ebeam2->ebeamLTUPosX()
          << std::setw(40) << ebeam2->ebeamLTUPosY()
          << std::setw(40) << ebeam2->ebeamLTUAngX()
          << std::setw(40) << ebeam2->ebeamLTUAngY()
          << std::setw(40) << ebeam2->ebeamPkCurrBC2()
           << std::setw(40) << ebeam2->ebeamEnergyBC2();
  }

  shared_ptr<Psana::Bld::BldDataEBeamV3> ebeam3 = evt.get(m_ebeamSrc);
  if (ebeam3) {
      _str << std::showbase << std::hex << std::setw(40) << ebeam3->damageMask() << std::dec
          << std::setw(40) << ebeam3->ebeamCharge()
          << std::setw(40) << ebeam3->ebeamL3Energy()
          << std::setw(40) << ebeam3->ebeamLTUPosX()
          << std::setw(40) << ebeam3->ebeamLTUPosY()
          << std::setw(40) << ebeam3->ebeamLTUAngX()
          << std::setw(40) << ebeam3->ebeamLTUAngY()
          << std::setw(40) << ebeam3->ebeamPkCurrBC2()
          << std::setw(40) << ebeam3->ebeamEnergyBC2()
          << std::setw(40) << ebeam3->ebeamPkCurrBC1()
           << std::setw(40) << ebeam3->ebeamEnergyBC1();
  }

  shared_ptr<Psana::Bld::BldDataEBeamV4> ebeam4 = evt.get(m_ebeamSrc);
  if (ebeam4) {
      _str << std::showbase << std::hex << std::setw(40) << ebeam4->damageMask() << std::dec
          << std::setw(40) << ebeam4->ebeamCharge()
          << std::setw(40) << ebeam4->ebeamL3Energy()
          << std::setw(40) << ebeam4->ebeamLTUPosX()
          << std::setw(40) << ebeam4->ebeamLTUPosY()
          << std::setw(40) << ebeam4->ebeamLTUAngX()
          << std::setw(40) << ebeam4->ebeamLTUAngY()
          << std::setw(40) << ebeam4->ebeamPkCurrBC2()
          << std::setw(40) << ebeam4->ebeamEnergyBC2()
          << std::setw(40) << ebeam4->ebeamPkCurrBC1()
          << std::setw(40) << ebeam4->ebeamEnergyBC1()
          << std::setw(40) << ebeam4->ebeamUndPosX()
          << std::setw(40) << ebeam4->ebeamUndPosY()
          << std::setw(40) << ebeam4->ebeamUndAngX()
           << std::setw(40) << ebeam4->ebeamUndAngY();
  }

  shared_ptr<Psana::Bld::BldDataPhaseCavity> cav = evt.get(m_cavSrc);
  if (cav) {
      _str << std::setw(40) << cav->fitTime1()
          << std::setw(40) << cav->fitTime2()
          << std::setw(40) << cav->charge1()
           << std::setw(40) << cav->charge2();
  }
  
  shared_ptr<Psana::Bld::BldDataFEEGasDetEnergy> fee = evt.get(m_feeSrc);
  if (fee) {
      _str << std::setw(40) << fee->f_11_ENRC()
          << std::setw(40) << fee->f_12_ENRC()
          << std::setw(40) << fee->f_21_ENRC()
           << std::setw(40) << fee->f_22_ENRC();
  }

  // dump BldDataGMDV0
  shared_ptr<Psana::Bld::BldDataGMDV0> gmd0 = evt.get(m_gmdSrc);
  if (gmd0) {
      _str
          << std::setw(40) << gmd0->gasType()
          << std::setw(40) << gmd0->pressure()
          << std::setw(40) << gmd0->temperature()
          << std::setw(40) << gmd0->current()
          << std::setw(40) << gmd0->hvMeshElectron()
          << std::setw(40) << gmd0->hvMeshIon()
          << std::setw(40) << gmd0->hvMultIon()
          << std::setw(40) << gmd0->chargeQ()
          << std::setw(40) << gmd0->photonEnergy()
          << std::setw(40) << gmd0->multPulseIntensity()
          << std::setw(40) << gmd0->keithleyPulseIntensity()
          << std::setw(40) << gmd0->pulseEnergy()
          << std::setw(40) << gmd0->pulseEnergyFEE()
          << std::setw(40) << gmd0->transmission()
          << std::setw(40) << gmd0->transmissionFEE();
  }

  // dump BldDataGMDV1
  shared_ptr<Psana::Bld::BldDataGMDV1> gmd1 = evt.get(m_gmdSrc);
  if (gmd1) {
      _str
          << std::setw(40) << gmd1->milliJoulesPerPulse()
          << std::setw(40) << gmd1->milliJoulesAverage()
          << std::setw(40) << gmd1->correctedSumPerPulse()
          << std::setw(40) << gmd1->bgValuePerSample()
          << std::setw(40) << gmd1->relativeEnergyPerPulse();
  }

  // dump BldDataSpectrometerV0
  shared_ptr<Psana::Bld::BldDataSpectrometerV0> spec0 = evt.get(m_gmdSrc);
  if (spec0) {
      _str 
          << std::setw(40) << spec0->hproj()
          << std::setw(40) << spec0->vproj();
  }

}

void 
DumpSmallData::dumpEpicsNames(Event& evt, Env& env)
{
  const EpicsStore& estore = env.epicsStore();
  std::vector<std::string> pvNames = estore.pvNames();
  size_t size = pvNames.size();

  for (size_t i = 0; i < size; ++ i) {
    shared_ptr<Psana::Epics::EpicsPvHeader> pv = estore.getPV(pvNames[i]);
    if (pv->numElements()==1) _str << std::setw(40) << pvNames[i];
  }
}

void
DumpSmallData::replaceAll(std::string& str, const std::string& from, const std::string& to) { 
  if(from.empty()) 
    return; 
  size_t start_pos = 0; 
  while((start_pos = str.find(from, start_pos)) != std::string::npos) { 
    str.replace(start_pos, from.length(), to); 
    start_pos += to.length(); // In case 'to' contains 'from', like replacing 'x' with 'yx' 
  } 
} 

void 
DumpSmallData::dumpEpicsValues(Event& evt, Env& env) {
  const EpicsStore& estore = env.epicsStore();
  std::vector<std::string> pvNames = estore.pvNames();
  size_t size = pvNames.size();

  for (size_t i = 0; i < size; ++ i) {
    
    // get generic PV object, only useful if you want to access
    // its type, and array size
    shared_ptr<Psana::Epics::EpicsPvHeader> pv = estore.getPV(pvNames[i]);
    if (pv->numElements()!=1) continue;
    const std::string& value = estore.value(pvNames[i], 0);
    std::string valuecopy(value);
    replaceAll(valuecopy," ","_");
//     if (pvNames[i]==savedNames[i])
      _str << std::setw(40) << valuecopy;
//     else
//       _str << " -";
  }
}

} // namespace cpo
