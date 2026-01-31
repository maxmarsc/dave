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

constexpr auto kBlockSize = 3;

//==============================================================================
static void arrayAndStaticSpan() {
  /// arrayAndStaticSpan::0
  std::array<float, kBlockSize> array_f                 = {0.F, 0.F, 0.F};
  std::array<std::complex<float>, kBlockSize> array_c   = {kCpxZeroF, kCpxZeroF,
                                                           kCpxZeroF};
  std::array<double, kBlockSize> array_d                = {0., 0., 0.};
  std::array<std::complex<double>, kBlockSize> array_cd = {kCpxZeroD, kCpxZeroD,
                                                           kCpxZeroD};
  auto span_f                                           = std::span(array_f);
  auto span_c                                           = std::span(array_c);
  auto span_d                                           = std::span(array_d);
  auto span_cd                                          = std::span(array_cd);

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

static void arrayAndStaticSpan2D() {
  /// arrayAndStaticSpan2D::0
  constexpr auto kChannels = 2;
  // std::arrays
  auto array_array_f = std::array{std::array<float, kBlockSize>{},
                                  std::array<float, kBlockSize>{}};
  auto array_span_f =
      std::array{std::span(array_array_f[0]), std::span(array_array_f[1])};
  auto array_vector_d = std::array<std::vector<double>, kChannels>{
      std::vector<double>(kBlockSize), std::vector<double>(kBlockSize)};
  auto array_dynspan_d =
      std::array{std::span(array_vector_d[0]), std::span(array_vector_d[1])};
  // 2d static spans
  [[maybe_unused]] auto span_array_f   = std::span(array_array_f);
  [[maybe_unused]] auto span_span_f    = std::span(array_span_f);
  [[maybe_unused]] auto span_vector_d  = std::span(array_vector_d);
  [[maybe_unused]] auto span_dynspan_d = std::span(array_dynspan_d);
  /// arrayAndStaticSpan2D::1
  array_array_f[1][0]  = 1.F;
  array_vector_d[1][0] = 1.;
  array_array_f[1][1]  = -1.F;
  array_vector_d[1][1] = -1.;
  /// arrayAndStaticSpan2D::2
}

static void vectorAndDynSpan2D() {
  /// vectorAndDynSpan2D::0
  constexpr auto kChannels = 2;
  // 2D std::vector
  auto vector_array_f = std::vector<std::array<float, kBlockSize>>(kChannels);
  // vector of static spans
  auto vector_span_f = std::vector<std::span<float, kBlockSize>>{
      std::span(vector_array_f[0]), std::span(vector_array_f[1])};
  // vector of vectors
  auto vector_vector_d = std::vector<std::vector<double>>(
      kChannels, std::vector<double>(kBlockSize));
  // vector of dyn spans
  auto vector_span_d = std::vector<std::span<double>>{
      std::span(vector_vector_d[0]), std::span(vector_vector_d[1])};
  // 2D dyn spans
  [[maybe_unused]] auto span_array_f  = std::span(vector_array_f);
  [[maybe_unused]] auto span_span_f   = std::span(vector_span_f);
  [[maybe_unused]] auto span_vector_d = std::span(vector_vector_d);
  [[maybe_unused]] auto span_span_d   = std::span(vector_span_d);
  /// vectorAndDynSpan2D::1
  vector_array_f[1][0]  = 1.F;
  vector_vector_d[1][0] = 1.;
  vector_array_f[1][1]  = -1.F;
  vector_vector_d[1][1] = -1.;
  /// vectorAndDynSpan2D::2
}

static void cArray() {
  /// cArray::0
  float array_f[kBlockSize]        = {0.F, 0.F, 0.F};
  std::complex<float> array_c[3]   = {kCpxZeroF, kCpxZeroF, kCpxZeroF};
  double array_d[kBlockSize]       = {0., 0., 0.};
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

static void numericValues() {
  /// numericValues::0
  std::array<float, kBlockSize> array_f                 = {0.F, 0.F, 0.F};
  std::array<std::complex<float>, kBlockSize> array_c   = {kCpxZeroF, kCpxZeroF,
                                                           kCpxZeroF};
  std::array<double, kBlockSize> array_d                = {0., 0., 0.};
  std::array<std::complex<double>, kBlockSize> array_cd = {kCpxZeroD, kCpxZeroD,
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

static void vectorAndDynSpan() {
  /// vectorAndDynSpan::0
  auto vector_f  = std::vector(kBlockSize, 0.F);
  auto vector_c  = std::vector(kBlockSize, kCpxZeroF);
  auto vector_d  = std::vector(kBlockSize, 0.);
  auto vector_cd = std::vector(kBlockSize, kCpxZeroD);
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
  arrayAndStaticSpan2D();
  vectorAndDynSpan2D();
  return 0;
}