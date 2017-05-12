#ifndef CPO_CSPAD2X2IMAGEPRODMANY_H
#define CPO_CSPAD2X2IMAGEPRODMANY_H

//--------------------------------------------------------------------------
// File and Version Information:
// 	$Id$
//
// Description:
//	Class CSPad2x2ImageProdMany.
//
//------------------------------------------------------------------------

//-----------------
// C/C++ Headers --
//-----------------

//----------------------
// Base Class Headers --
//----------------------
#include "psana/Module.h"
#include "MsgLogger/MsgLogger.h"

//-------------------------------
// Collaborating Class Headers --
//-------------------------------
#include "PSCalib/CSPad2x2CalibPars.h"
#include "CSPadPixCoords/PixCoordsCSPad2x2V2.h"
#include "CSPadPixCoords/GlobalMethods.h"

#include <boost/gil/gil_all.hpp>
#ifndef BOOST_GIL_NO_IO
#include <boost/gil/extension/io/png_io.hpp> 
#include <boost/gil/extension/io/tiff_io.hpp> 
//#include <boost/gil/extension/io/jpeg_io.hpp>

#include <boost/gil/extension/io/png_dynamic_io.hpp>
#include <boost/gil/extension/io/tiff_dynamic_io.hpp> 
//#include <boost/gil/extension/io/jpeg_dynamic_io.hpp> 
#endif
//------------------------------------
// Collaborating Class Declarations --
//------------------------------------

#include "PSEvt/Source.h"


//		---------------------
// 		-- Class Interface --
//		---------------------

using namespace CSPadPixCoords;

namespace cpo {

/// @addtogroup cpo

/**
 *  @ingroup cpo
 *
 *  @brief CSPad2x2ImageProdMany produces the CSPad2x2 image for each event and add it to the event in psana framework.
 *
 *  CSPad2x2ImageProdMany works in psana framework. It does a few operation as follows:
 *  1) get the pixel coordinates from PixCoords2x1 and PixCoordsCSPad2x2 classes,
 *  2) get data from the event,
 *  3) produce the Image2D object with CSPad image for each event,
 *  4) add the Image2D object in the event for further modules.
 *
 *  The CSPad2x2 image array currently is shaped as [400][400] pixels.
 *
 *  This class should not be used directly in the code of users modules. 
 *  Instead, it should be added as a module in the psana.cfg file with appropriate parameters.
 *  Then, the produced Image2D object can be extracted from event and used in other modules.
 *
 *  This software was developed for the LCLS project.  If you use all or 
 *  part of it, please give an appropriate acknowledgment.
 *
 *  @see PixCoords2x1, PixCoordsQuad, PixCoordsCSPad, CSPadImageGetTest
 *
 *  @version \$Id$
 *
 *  @author Mikhail S. Dubrovin
 */

class CSPad2x2ImageProdMany : public Module {
public:

  typedef CSPadPixCoords::PixCoordsCSPad2x2V2 PC2X2;

  const static int NX_CSPAD2X2=400; 
  const static int NY_CSPAD2X2=400;

  // Default constructor
  CSPad2x2ImageProdMany (const std::string& name) ;

  // Destructor
  virtual ~CSPad2x2ImageProdMany () ;

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

  void printInputParameters();
  void getConfigPars(Env& env);
  void getCalibPars(Event& evt, Env& env);
  void cspad_image_init();
  void processEvent(Event& evt, Env& env);

  //void cspad_image_fill(const int16_t* data, CSPadPixCoords::QuadParameters* quadpars, PSCalib::CSPadCalibPars *cspad_calibpar);
  void cspad_image_fill(const ndarray<const int16_t,3>& data);
  void cspad_image_add_in_event(Event& evt);
  void checkTypeImplementation();

private:

  // Data members, this is for example purposes only

  std::string m_calibDir;       // i.e. ./calib
  std::string m_typeGroupName;  // i.e. CsPad2x2::CalibV1
  //std::string m_str_src;        // i.e. MecTargetChamber.0:Cspad2x2.1
  Source      m_source;         // i.e. Detinfo(MecTargetChamber.0:Cspad2x2.1)
  Pds::Src    m_src;
  std::string m_inkey; 
  std::string m_outimgkey;      // i.e. "CSPad:Image"
  std::string m_outtype;
  std::string m_fname;
  bool        m_tiltIsApplied;
  bool        m_useWidePixCenter; 
  unsigned    m_print_bits;
  unsigned    m_count_cfg;

  uint32_t m_roiMask;
  uint32_t m_numAsicsStored;

  PSCalib::CSPad2x2CalibPars  *m_cspad2x2_calibpars;
  PC2X2                       *m_pix_coords_cspad2x2;

  uint32_t   m_cspad_ind;
  double    *m_coor_x_pix;
  double    *m_coor_y_pix;
  uint32_t  *m_coor_x_int;
  uint32_t  *m_coor_y_int;

  float      m_common_mode[2];

  int16_t m_arr_cspad2x2_image[NX_CSPAD2X2][NY_CSPAD2X2];


public:

  /**
   * @brief Get configuration info from Env, return true if configuration is found, othervise false.
   * 
   */

  //--------------------
  /// Save 2-D array in TIFF file
  template <typename T>
    bool save2DArrayInTIFFForType(const std::string& fname, const T* arr, const unsigned& rows, const unsigned& cols)
    {
      using namespace boost::gil;

      unsigned size = cols*rows;

      if ( *typeid(T).name() == *typeid(double).name() ) {
        float* arr32f = new float[size]; 
        for (unsigned i=0; i<size; i++) { arr32f[i] = (float)arr[i]; }
        gray32f_view_t image = interleaved_view(cols, rows, (gray32f_pixel_t*)&arr32f[0], cols*sizeof(float));
        tiff_write_view(fname, image);
        return true;
      }

      else if ( *typeid(T).name() == *typeid(float).name() ) {
        float* p_arr = (float*)&arr[0];
        gray32f_view_t image = interleaved_view(cols, rows, (gray32f_pixel_t*)p_arr, cols*sizeof(T));
        tiff_write_view(fname, image);
        return true;
      }

      else if ( *typeid(T).name() == *typeid(int).name() ) {
        //int* p_arr = (int*)&arr[0];
        //gray32c_view_t image = interleaved_view(cols, rows, reinterpret_cast<const gray32_pixel_t*>(p_arr), cols*sizeof(T));
        float* arr32f = new float[size]; 
        for (unsigned i=0; i<size; i++) { arr32f[i] = (int)arr[i]; }
        gray32f_view_t image = interleaved_view(cols, rows, (gray32f_pixel_t*)&arr32f[0], cols*sizeof(float));
        tiff_write_view(fname, image);
        return true;
      }

      else if ( *typeid(T).name() == *typeid(uint16_t).name() ) {
        uint16_t* p_arr = (uint16_t*)&arr[0];
        gray16c_view_t image = interleaved_view(cols, rows, (const gray16_pixel_t*)p_arr, cols*sizeof(T));
        tiff_write_view(fname, image);
        return true;
      }

      else if ( *typeid(T).name() == *typeid(int16_t).name() ) {
        int16_t* p_arr = (int16_t*)&arr[0];
        gray16c_view_t image = interleaved_view(cols, rows, (const gray16_pixel_t*)p_arr, cols*sizeof(T));
        tiff_write_view(fname, image);
        return true;
      }

      else if ( *typeid(T).name() == *typeid(uint8_t).name() ) {
        uint8_t* p_arr = (uint8_t*)&arr[0];
        gray8c_view_t image = interleaved_view(cols, rows, (const gray8_pixel_t*)p_arr, cols*sizeof(T));
        tiff_write_view(fname, image);
        png_write_view(fname+".png", image);
        return true;
      }

      return false;
    }
//--------------------

  template <typename T>
  bool getConfigParsForType(Env& env)
  {
      shared_ptr<T> config = env.configStore().get(m_source, &m_src);
      if (config) {
        m_roiMask        = config->roiMask();
        m_numAsicsStored = config->numAsicsStored();
        ++ m_count_cfg;
        WithMsgLog(name(), info, str) {
          str << "CsPad2x2::ConfigV"    << m_count_cfg << ":";
          str << " roiMask = "          << config->roiMask();
          str << " m_numAsicsStored = " << config->numAsicsStored();
         }  
	return true;
      }
      return false;
  }
//--------------------

  template <typename TOUT>
  void save2DArrayInEventForType (Event& evt) {

      string fname = m_fname
        + "-r"    + stringRunNumber(evt) 
        + "-"     + stringTimeStamp(evt) 
        + ".tiff";

      const unsigned shape[] = {NX_CSPAD2X2, NY_CSPAD2X2};
      ndarray<int16_t,2> img_nda (&m_arr_cspad2x2_image[0][0],shape);
      
      if (typeid(TOUT) == typeid(double)) { // typeid(double).name()
        save2DArrayInTIFFForType(fname,img_nda.data(),img_nda.shape()[0],
                                 img_nda.shape()[1]);
        return;
      }
      
      ndarray<TOUT,2> img_out (shape);
      
      //Copy array with type changing
      typename ndarray<TOUT,2>::iterator it_out = img_out.begin(); 
      for ( ndarray<const int16_t,2>::iterator it=img_nda.begin(); it!=img_nda.end(); ++it, ++it_out ) {
        *it_out = (TOUT)*it;
      }

      save2DArrayInTIFFForType(fname,img_nda.data(),img_nda.shape()[0],
                               img_nda.shape()[1]);
  }

}; // class CSPad2x2ImageProdMany

} // namespace cpo

#endif // CPO_CSPAD2X2IMAGEPRODMANY_H
