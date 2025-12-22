#include <array>
#include <cmath>
#include <complex>
#include <span>
#include <vector>

#include "numerics.hpp"

/**
 * @brief File used to unit test the STD features of DAVE
 * @warning DO NOT MODIFY THIS FILE
 *
 * @note Since the tests are relying on precise line numbers, a hash check is
 * performed on the content of this file. If you modify this file in any way
 * be very careful and update the hash in the tests.
 */

//==============================================================================
void arrayAndStaticSpan() {
  /// arrayAndStaticSpan::0
  std::array<float, 3> array_f                 = {0.F, 0.F, 0.F};
  std::array<std::complex<float>, 3> array_c   = {kCpxZeroF, kCpxZeroF,
                                                  kCpxZeroF};
  std::array<double, 3> array_d                = {0., 0., 0.};
  std::array<std::complex<double>, 3> array_cd = {kCpxZeroD, kCpxZeroD,
                                                  kCpxZeroD};
  auto span_f                                  = std::span(array_f);
  auto span_c                                  = std::span(array_c);
  auto span_d                                  = std::span(array_d);
  auto span_cd                                 = std::span(array_cd);

  /// arrayAndStaticSpan::1
  array_f[0]  = 1.F;
  array_d[0]  = 1.;
  array_c[0]  = kCpxOneF;
  array_cd[0] = kCpxOneD;
  array_f[1]  = -1.F;
  array_d[1]  = -1.;
  array_c[1]  = kCpxMinusOneF;
  array_cd[1] = kCpxMinusOneD;
  /// arrayAndStaticSpan::2
}

void cArray() {
  /// cArray::0
  float array_f[3]                 = {0.F, 0.F, 0.F};
  std::complex<float> array_c[3]   = {kCpxZeroF, kCpxZeroF, kCpxZeroF};
  double array_d[3]                = {0., 0., 0.};
  std::complex<double> array_cd[3] = {kCpxZeroD, kCpxZeroD, kCpxZeroD};

  /// cArray::1
  array_f[0]  = 1.F;
  array_d[0]  = 1.;
  array_c[0]  = kCpxOneF;
  array_cd[0] = kCpxOneD;
  array_f[1]  = -1.F;
  array_d[1]  = -1.;
  array_c[1]  = kCpxMinusOneF;
  array_cd[1] = kCpxMinusOneD;
  /// cArray::2
}

void numericValues() {
  /// numericValues::0
  std::array<float, 3> array_f                 = {0.F, 0.F, 0.F};
  std::array<std::complex<float>, 3> array_c   = {kCpxZeroF, kCpxZeroF,
                                                  kCpxZeroF};
  std::array<double, 3> array_d                = {0., 0., 0.};
  std::array<std::complex<double>, 3> array_cd = {kCpxZeroD, kCpxZeroD,
                                                  kCpxZeroD};

  /// numericValues::1
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
  /// numericValues::2
}

void vectorAndDynSpan() {
  /// vectorAndDynSpan::0
  auto vector_f  = std::vector(3, 0.F);
  auto vector_c  = std::vector(3, kCpxZeroF);
  auto vector_d  = std::vector(3, 0.);
  auto vector_cd = std::vector(3, kCpxZeroD);
  auto span_f    = std::span(vector_f);
  auto span_c    = std::span(vector_c);
  auto span_d    = std::span(vector_d);
  auto span_cd   = std::span(vector_cd);

  /// vectorAndDynSpan::1
  vector_f[0]  = 1.F;
  vector_d[0]  = 1.;
  vector_c[0]  = kCpxOneF;
  vector_cd[0] = kCpxOneD;
  vector_f[1]  = -1.F;
  vector_d[1]  = -1.;
  vector_c[1]  = kCpxMinusOneF;
  vector_cd[1] = kCpxMinusOneD;
  /// vectorAndDynSpan::2
  vector_f.resize(2);
  vector_c.resize(2);
  vector_d.resize(2);
  vector_cd.resize(2);
  span_f  = std::span(vector_f);
  span_c  = std::span(vector_c);
  span_d  = std::span(vector_d);
  span_cd = std::span(vector_cd);
  /// vectorAndDynSpan::3
  vector_f.resize(4);
  vector_c.resize(4);
  vector_d.resize(4);
  vector_cd.resize(4);
  span_f  = std::span(vector_f);
  span_c  = std::span(vector_c);
  span_d  = std::span(vector_d);
  span_cd = std::span(vector_cd);
  /// vectorAndDynSpan::4
}

int main() {
  arrayAndStaticSpan();
  cArray();
  numericValues();
  vectorAndDynSpan();
  return 0;
}