#include <array>
#include <cmath>

constexpr auto kBlockSize = 4096;
constexpr auto kTEst      = kBlockSize / 100;

int main() {
  float carray[kBlockSize]{};
  double carray_d[kBlockSize]{};
  auto array     = std::array<float, kBlockSize>{};
  auto& carray_r = carray;
  auto& array_r  = array;

  // Fill with zeros
  std::fill(carray, carray + kBlockSize, 0.F);
  std::fill(array.begin(), array.end(), 0.F);

  // Fill with std::sin
  auto step  = 2.F * M_PIf / kBlockSize * 16;
  auto phase = 0.F;
  for (auto i = 0; i < kBlockSize; ++i) {
    auto val    = std::sin(phase);
    carray[i]   = val;
    carray_d[i] = val;
    array[i]    = -val;
    phase += step;
    if (i % 8 == 0)
      step *= 1.01F;
  }

  // Apply 0.5 gain
  for (auto i = 0; i < kBlockSize; ++i) {
    carray[i] *= 0.5F;
    array[i] *= 0.5F;
  }

  return 0;
}