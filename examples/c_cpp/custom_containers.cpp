#include <cmath>
#include <vector>

#include "custom_containers.hpp"

constexpr auto kBlockSize = 4096;
constexpr auto kChannels  = 2;

int main() {
  //==============================================================================
  auto vector = std::vector<float>(kBlockSize * kChannels);

  // DaveCustomContainerPtr
  auto ccptr = DaveCustomContainerPtr<float>{vector.data(), kBlockSize};

  // DaveCustomContainerPtrPtr
  float* ptr_carray[] = {vector.data(), vector.data() + kBlockSize};
  auto ccptrptr = DaveCustomContainerPtrPtr{ptr_carray, kBlockSize, kChannels};

  // DaveCustomInterleavedContainerVec
  auto ccvec = DaveCustomInterleavedContainerVec{vector, kBlockSize, kChannels};

  // DaveCustomContainerVecRef
  auto ccvecref = DaveCustomContainerVecRef{vector, kBlockSize, kChannels};

  // Fill with values
  std::fill(vector.begin(), vector.end(), -1.F);
  std::fill(ccvec.vec_.begin(), ccvec.vec_.end(), .5F);

  // Fill with std::sin
  auto step  = 3.14F / kBlockSize * 4;
  auto phase = 0.F;

  for (auto i = 0; i < kBlockSize * kChannels; ++i) {
    auto val      = std::sin(phase);
    vector[i]     = val;
    ccvec.vec_[i] = -val;
    phase += step;
    if (i % 8 == 0)
      step *= 1.01F;
  }

  // Apply gain
  for (auto i = 0; i < kBlockSize * kChannels; ++i) {
    vector[i] *= .5F;
    ccvec.vec_[i] *= 0.75F;
  }

  return 0;
}