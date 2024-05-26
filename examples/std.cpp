#include <array>
#include <cmath>
#include <complex>
#include <span>
#include <vector>

constexpr auto kBlockSize = 4096;

int main() {
  float carray[kBlockSize]{};
  double carray_d[kBlockSize]{};
  std::complex<float> carray_cpx[kBlockSize]{};
  auto array      = std::array<float, kBlockSize>{};
  auto cpx_array  = std::array<std::complex<float>, kBlockSize>{};
  auto vector     = std::vector<float>(kBlockSize);
  auto cpx_vector = std::vector<std::complex<float>>(kBlockSize);
  auto span       = std::span(vector);
  auto cpx_span   = std::span(cpx_vector);
  auto& carray_r  = carray;
  auto& array_r   = array;

  // Fill with zeros
  std::fill(carray, carray + kBlockSize, 0.F);
  std::fill(array.begin(), array.end(), 0.F);

  // Fill with std::sin
  auto step  = 2.F * M_PIf / kBlockSize * 16;
  auto phase = 0.F;
  for (auto i = 0; i < kBlockSize; ++i) {
    auto val      = std::sin(phase);
    carray[i]     = val;
    carray_d[i]   = val;
    array[i]      = -val;
    vector[i]     = val;
    carray_cpx[i] = val;
    phase += step;
    if (i % 8 == 0)
      step *= 1.01F;
  }

  // Apply 0.5 gain
  for (auto i = 0; i < kBlockSize; ++i) {
    carray[i] *= 0.5F;
    array[i] *= 0.5F;
    vector[i] *= 0.5F;
    carray_cpx[i] *= 0.5F;
  }

  return 0;
}