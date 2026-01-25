#include "custom_containers.hpp"
#include "numerics.hpp"

static void containerPrettyPrinters() {
  /// containerPrettyPrinters::0
  constexpr auto kBlockSize = 11;
  constexpr auto kChannels  = 2;
  auto vector               = std::vector<float>(kBlockSize * kChannels);
  float* ptr_carray[]       = {vector.data(), vector.data() + kBlockSize};

  auto container = DaveCustomContainerPtrPtr{ptr_carray, kBlockSize, kChannels};
  /// containerPrettyPrinters::1
  auto val        = 1.F;
  const auto step = 0.2F;
  for (auto i = 0; i < 11; ++i) {
    ptr_carray[0][i] = val;
    ptr_carray[1][i] = -val;
    val -= step;
  }
  /// containerPrettyPrinters::2
  ptr_carray[0][0]  = kPInfF;
  ptr_carray[0][1]  = 1.5F;
  ptr_carray[0][5]  = kNanF;
  ptr_carray[0][9]  = -1.5F;
  ptr_carray[0][10] = kNInfF;
  /// containerPrettyPrinters::3
}

static void daveCommands() {
  /// daveCommands::0
  constexpr auto kBlockSize = 3;
  constexpr auto kChannels  = 2;
  auto container            = DaveCustomInterleavedContainerVec{
      std::vector<float>(kBlockSize * kChannels), kBlockSize, kChannels};
  auto& container_ref = container;
  /// daveCommands::1
  container.vec_[0] = 1.0;
  /// daveCommands::2
}

int main() {
  containerPrettyPrinters();
  daveCommands();

  return 0;
}