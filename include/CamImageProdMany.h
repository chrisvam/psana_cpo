#ifndef CPO_CAMIMAGEPRODMANY_H
#define CPO_CAMIMAGEPRODMANY_H

//--------------------------------------------------------------------------
// File and Version Information:
// 	$Id$
//
// Description:
//	Class CamImageProdMany.
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

using namespace std;

namespace cpo {

class CamImageProdMany : public Module {
public:

  /// Default constructor
  CamImageProdMany (const std::string& name) ;

  /// Destructor
  virtual ~CamImageProdMany () ;

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

  void procEvent(Event& evt, Env& env);

private:

  // Data members, this is for example purposes only

  std::string m_str_src;        // i.e. CxiDs1.0:Cspad.0
   
  Source      m_source;         // Data source set from config file
  Pds::Src    m_src;
  std::string m_fname;

  ndarray<double,2> m_data;

  /*
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
  */

//-------------------

};

} // namespace cpo

#endif // CPO_CAMIMAGEPRODUCER_H
