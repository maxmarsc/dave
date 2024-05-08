#include <array>
#include <cmath>

constexpr auto kBlockSize = 256;

int main() {
  float carray[kBlockSize]{};
  auto array     = std::array<float, kBlockSize>{};
  auto& carray_r = carray;
  auto& array_r  = array;

  // Fill with zeros
  std::fill(carray, carray + kBlockSize, 0.F);
  std::fill(array.begin(), array.end(), 0.F);

  // Fill with std::sin
  const auto step = 2.F * M_PIf / kBlockSize;
  auto phase      = 0.F;
  for (auto i = 0; i < kBlockSize; ++i) {
    auto val  = std::sin(phase);
    carray[i] = val;
    array[i]  = -val;
    phase += step;
  }

  // Apply 0.5 gain
  for (auto i = 0; i < kBlockSize; ++i) {
    carray[i] *= 0.5F;
    array[i] *= 0.5F;
  }

  return 0;
}