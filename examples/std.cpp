#include <array>
#include <cmath>
#include <complex>
#include <span>
#include <vector>

constexpr auto kBlockSize = 4096;
constexpr auto kChannels  = 2;

int main() {
  //============================================================================
  float carray[kBlockSize]{};
  float carray_carray[kChannels][kBlockSize]{};
  float* carray_ptr[kChannels]{carray_carray[0], carray_carray[1]};
  auto** ptr_ptr = carray_ptr;

  //============================================================================
  std::vector<float> carray_vector[kChannels] = {
      std::vector<float>(kBlockSize), std::vector<float>(kBlockSize)};
  std::array<float, kBlockSize> carray_array[kChannels] = {};
  std::span<float> carray_span[kChannels] = {carray_array[1], carray_vector[1]};
  double carray_d[kBlockSize]             = {};
  std::complex<float> carray_cpx[kBlockSize] = {};

  //==============================================================================
  auto array_array  = std::array<std::array<float, kBlockSize>, kChannels>{};
  auto array_vector = std::array<std::vector<float>, kChannels>{
      std::vector<float>(kBlockSize), std::vector<float>(kBlockSize)};
  auto array_span =
      std::array<std::span<float>, kChannels>{array_vector[0], array_array[0]};

  //==============================================================================
  auto vector_array  = std::vector<std::array<float, kBlockSize>>{kChannels};
  auto vector_vector = std::vector<std::vector<float>>{
      std::vector<float>(kBlockSize), std::vector<float>(kBlockSize)};
  auto vector_span =
      std::vector<std::span<float>>{vector_vector[0], vector_array[0]};

  //==============================================================================
  auto span_array  = std::span{array_array};
  auto span_vector = std::span{vector_vector};
  auto span_span   = std::span{vector_span};

  //============================================================================
  auto array      = std::array<float, kBlockSize>{};
  auto cpx_array  = std::array<std::complex<float>, kBlockSize>{};
  auto vector     = std::vector<float>(kBlockSize);
  auto cpx_vector = std::vector<std::complex<float>>(kBlockSize);
  auto span       = std::span(vector);
  auto cpx_span   = std::span(cpx_vector);
  auto& carray_r  = carray;
  auto& array_r   = array;
  auto* ptr       = carray;
  auto* cpx_ptr   = cpx_array.data();

  // Fill with zeros
  std::fill(carray, carray + kBlockSize, 0.F);
  std::fill(array.begin(), array.end(), 0.F);

  // Fill with std::sin
  auto step  = 2.F * 3.14F / kBlockSize * 16;
  auto phase = 0.F;
  for (auto i = 0; i < kBlockSize; ++i) {
    auto val            = std::sin(phase);
    carray[i]           = val;
    carray_carray[0][i] = val;
    carray_array[0][i]  = val * val;
    carray_vector[0][i] = -val * val;
    carray_vector[1][i] = val / 2;
    carray_span[0][i]   = -val;
    carray_d[i]         = val;
    array[i]            = -val;
    vector[i]           = val;
    carray_cpx[i]       = val;
    phase += step;
    if (i % 8 == 0)
      step *= 1.01F;
  }

  // Apply 0.5 gain
  for (auto i = 0; i < kBlockSize; ++i) {
    carray[i] *= 1.5F;
    array[i] *= 0.5F;
    vector[i] *= 0.5F;
    carray_cpx[i] *= 0.5F;
    carray_vector[0][i] *= 0.5F;
    carray_vector[1][i] *= 0.5F;
  }

  return 0;
}