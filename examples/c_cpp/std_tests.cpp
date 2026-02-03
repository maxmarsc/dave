#include <array>
#include <cmath>
#include <complex>
#include <vector>
#ifdef USE_GSL
#include <gsl/span>
#define SPAN_SRC gsl
#else
#include <span>
#define SPAN_SRC std
#endif

#include "numerics.hpp"
#include "test_utils.hpp"

/**
 * @brief File used to unit test the server-side features of DAVE
 * @warning BE CAREFUL WHEN EDITING THIS FILE
 * 
 * @details The tests uses automatic parsing of the source code to identify
 * "tags" ie: //// <tag>::<index>
 * A tag is used to indicate a relevant location to place a breakpoint.
 */

constexpr auto kBlockSize = 3;

//==============================================================================
static void arrayAndStaticSpan() {
  //// arrayAndStaticSpan::0
  std::array<float, kBlockSize> array_f                 = {0.F, 0.F, 0.F};
  std::array<std::complex<float>, kBlockSize> array_c   = {kCpxZeroF, kCpxZeroF,
                                                           kCpxZeroF};
  std::array<double, kBlockSize> array_d                = {0., 0., 0.};
  std::array<std::complex<double>, kBlockSize> array_cd = {kCpxZeroD, kCpxZeroD,
                                                           kCpxZeroD};
  auto span_f  = SPAN_SRC::span(array_f);
  auto span_c  = SPAN_SRC::span(array_c);
  auto span_d  = SPAN_SRC::span(array_d);
  auto span_cd = SPAN_SRC::span(array_cd);

  //// arrayAndStaticSpan::1
  array_f[0]  = 1.F;
  array_d[0]  = 1.;
  array_c[0]  = kCpxOneF;
  array_cd[0] = kCpxOneD;
  array_f[1]  = -1.F;
  array_d[1]  = -1.;
  array_c[1]  = kCpxMinusOneF;
  array_cd[1] = kCpxMinusOneD;
  //// arrayAndStaticSpan::2
  BREAKABLE_END;
}

static void arrayAndStaticSpan2D() {
  //// arrayAndStaticSpan2D::0
  constexpr auto kChannels = 2;
  // std::arrays
  auto array_array_f  = std::array{std::array<float, kBlockSize>{},
                                  std::array<float, kBlockSize>{}};
  auto array_span_f   = std::array{SPAN_SRC::span(array_array_f[0]),
                                 SPAN_SRC::span(array_array_f[1])};
  auto array_vector_d = std::array<std::vector<double>, kChannels>{
      std::vector<double>(kBlockSize), std::vector<double>(kBlockSize)};
  auto array_dynspan_d = std::array{SPAN_SRC::span(array_vector_d[0]),
                                    SPAN_SRC::span(array_vector_d[1])};
  // 2d static spans
  [[maybe_unused]] auto span_array_f   = SPAN_SRC::span(array_array_f);
  [[maybe_unused]] auto span_span_f    = SPAN_SRC::span(array_span_f);
  [[maybe_unused]] auto span_vector_d  = SPAN_SRC::span(array_vector_d);
  [[maybe_unused]] auto span_dynspan_d = SPAN_SRC::span(array_dynspan_d);
  //// arrayAndStaticSpan2D::1
  array_array_f[1][0]  = 1.F;
  array_vector_d[1][0] = 1.;
  array_array_f[1][1]  = -1.F;
  array_vector_d[1][1] = -1.;
  //// arrayAndStaticSpan2D::2
  BREAKABLE_END;
}

static void vectorAndDynSpan2D() {
  //// vectorAndDynSpan2D::0
  constexpr auto kChannels = 2;
  // 2D std::vector
  auto vector_array_f = std::vector<std::array<float, kBlockSize>>(kChannels);
  // vector of static spans
  auto vector_span_f = std::vector<SPAN_SRC::span<float, kBlockSize>>{
      SPAN_SRC::span(vector_array_f[0]), SPAN_SRC::span(vector_array_f[1])};
  // vector of vectors
  auto vector_vector_d = std::vector<std::vector<double>>(
      kChannels, std::vector<double>(kBlockSize));
  // vector of dyn spans
  auto vector_span_d = std::vector<SPAN_SRC::span<double>>{
      SPAN_SRC::span(vector_vector_d[0]), SPAN_SRC::span(vector_vector_d[1])};
  // 2D dyn spans
  [[maybe_unused]] auto span_array_f  = SPAN_SRC::span(vector_array_f);
  [[maybe_unused]] auto span_span_f   = SPAN_SRC::span(vector_span_f);
  [[maybe_unused]] auto span_vector_d = SPAN_SRC::span(vector_vector_d);
  [[maybe_unused]] auto span_span_d   = SPAN_SRC::span(vector_span_d);
  //// vectorAndDynSpan2D::1
  vector_array_f[1][0]  = 1.F;
  vector_vector_d[1][0] = 1.;
  vector_array_f[1][1]  = -1.F;
  vector_vector_d[1][1] = -1.;
  //// vectorAndDynSpan2D::2
  BREAKABLE_END;
}

static void cArrayAndPtr() {
  //// cArrayAndPtr::0
  float array_f[kBlockSize]        = {0.F, 0.F, 0.F};
  std::complex<float> array_c[3]   = {kCpxZeroF, kCpxZeroF, kCpxZeroF};
  double array_d[kBlockSize]       = {0., 0., 0.};
  std::complex<double> array_cd[3] = {kCpxZeroD, kCpxZeroD, kCpxZeroD};
  float* ptr_f                     = array_f;
  double* ptr_d                    = array_d;
  std::complex<float>* ptr_c       = array_c;
  std::complex<double>* ptr_cd     = array_cd;

  //// cArrayAndPtr::1
  array_f[0]  = 1.F;
  array_d[0]  = 1.;
  array_c[0]  = kCpxOneF;
  array_cd[0] = kCpxOneD;
  array_f[1]  = -1.F;
  array_d[1]  = -1.;
  array_c[1]  = kCpxMinusOneF;
  array_cd[1] = kCpxMinusOneD;
  //// cArrayAndPtr::2
  BREAKABLE_END;
}

static void cArrayAndPtr2D() {
  //// cArrayAndPtr2D::0
  constexpr auto kChannels                    = 2;
  float array_array_f[kChannels][kBlockSize]  = {};
  double array_array_d[kChannels][kBlockSize] = {};
  float* array_ptrs_f[kChannels]  = {array_array_f[0], array_array_f[1]};
  double* array_ptrs_d[kChannels] = {array_array_d[0], array_array_d[1]};
  float** ptr_ptrs_f              = array_ptrs_f;
  double** ptr_ptrs_d             = array_ptrs_d;

  //// cArrayAndPtr2D::1
  array_array_f[1][0] = 1.F;
  array_array_d[1][0] = 1.;
  array_array_f[1][1] = -1.F;
  array_array_d[1][1] = -1.;
  //// cArrayAndPtr2D::2
  BREAKABLE_END;
}

static void numericValues() {
  //// numericValues::0
  std::array<float, kBlockSize> array_f                 = {0.F, 0.F, 0.F};
  std::array<std::complex<float>, kBlockSize> array_c   = {kCpxZeroF, kCpxZeroF,
                                                           kCpxZeroF};
  std::array<double, kBlockSize> array_d                = {0., 0., 0.};
  std::array<std::complex<double>, kBlockSize> array_cd = {kCpxZeroD, kCpxZeroD,
                                                           kCpxZeroD};

  //// numericValues::1
  array_f[0]  = kNanF;
  array_d[0]  = kNanD;
  array_c[0]  = std::complex(kNanF, 0.F);
  array_cd[0] = std::complex(kNanD, 0.);
  array_f[1]  = kPInfF;
  array_d[1]  = kPInfD;
  array_c[1]  = std::complex(kPInfF, 0.F);
  array_cd[1] = std::complex(kPInfD, 0.);
  array_f[2]  = kNInfF;
  array_d[2]  = kNInfD;
  array_c[2]  = std::complex(kNInfF, 0.F);
  array_cd[2] = std::complex(kNInfD, 0.0);
  //// numericValues::2
  BREAKABLE_END;
}

static void vectorAndDynSpan() {
  //// vectorAndDynSpan::0
  auto vector_f  = std::vector(kBlockSize, 0.F);
  auto vector_c  = std::vector(kBlockSize, kCpxZeroF);
  auto vector_d  = std::vector(kBlockSize, 0.);
  auto vector_cd = std::vector(kBlockSize, kCpxZeroD);
  auto span_f    = SPAN_SRC::span(vector_f);
  auto span_c    = SPAN_SRC::span(vector_c);
  auto span_d    = SPAN_SRC::span(vector_d);
  auto span_cd   = SPAN_SRC::span(vector_cd);

  //// vectorAndDynSpan::1
  vector_f[0]  = 1.F;
  vector_d[0]  = 1.;
  vector_c[0]  = kCpxOneF;
  vector_cd[0] = kCpxOneD;
  vector_f[1]  = -1.F;
  vector_d[1]  = -1.;
  vector_c[1]  = kCpxMinusOneF;
  vector_cd[1] = kCpxMinusOneD;
  //// vectorAndDynSpan::2
  vector_f.resize(2);
  vector_c.resize(2);
  vector_d.resize(2);
  vector_cd.resize(2);
  span_f  = SPAN_SRC::span(vector_f);
  span_c  = SPAN_SRC::span(vector_c);
  span_d  = SPAN_SRC::span(vector_d);
  span_cd = SPAN_SRC::span(vector_cd);
  //// vectorAndDynSpan::3
  vector_f.resize(4);
  vector_c.resize(4);
  vector_d.resize(4);
  vector_cd.resize(4);
  span_f  = SPAN_SRC::span(vector_f);
  span_c  = SPAN_SRC::span(vector_c);
  span_d  = SPAN_SRC::span(vector_d);
  span_cd = SPAN_SRC::span(vector_cd);
  //// vectorAndDynSpan::4
  BREAKABLE_END;
}

int main() {
  arrayAndStaticSpan();
  cArrayAndPtr();
  numericValues();
  vectorAndDynSpan();
  arrayAndStaticSpan2D();
  vectorAndDynSpan2D();
  cArrayAndPtr2D();
  return 0;
}