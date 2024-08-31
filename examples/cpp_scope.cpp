#include <array>
#include <memory>
#include <vector>

constexpr auto kBlockSize = 4096;

class A {
 public:
  void pouet() {
    vector_.resize(kBlockSize);
    std::fill(vector_.begin(), vector_.end(), -2.F);
    array_.fill(3.F);
    array_[0] += 1.F;
  }

 private:
  std::array<float, kBlockSize> array_{};
  std::vector<float> vector_{};
};

int main() {

  //============================================================================
  // Scope A
  {
    auto a = A{};
    a.pouet();
    auto array = std::array<float, kBlockSize>{};
    for (auto& val : array) {
      val = 1.F;
    }
    array.fill(0.5F);
    a.pouet();
  }

  // Scope B
  {
    auto vector = std::vector<float>(kBlockSize);
    for (auto& val : vector) {
      val = 1.F;
    }
    std::fill(vector.begin(), vector.end(), -1.F);
  }

  return 0;
}