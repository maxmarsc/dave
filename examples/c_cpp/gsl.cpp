#include <array>
#include <cmath>
#include <complex>
#include <gsl/span>
#include <span>
#include <vector>

constexpr auto kBlockSize = 4096;
constexpr auto kChannels  = 2;

int main() {
  auto array         = std::array<float, kBlockSize * kChannels>{};
  auto array_array   = std::array<std::array<float, kBlockSize>, kChannels>{};
  auto vector        = std::vector<float>(kBlockSize * kChannels);
  auto vector_vector = std::vector<std::vector<float>>{
      std::vector<float>(kBlockSize), std::vector<float>(kBlockSize)};

  //============================================================================
  // 1D
  auto static_span  = gsl::span<float, kBlockSize * kChannels>(array);
  auto dynamic_span = gsl::span<float>(vector);

  //============================================================================
  // 2D
  auto array_sspan = std::array<gsl::span<float, kBlockSize>, kChannels>{
      array_array[0], array_array[1]};
  auto sspan_sspan = gsl::span(array_sspan);
  auto vector_span =
      std::vector<gsl::span<float>>{vector_vector[0], vector_vector[0]};
  auto span_span = gsl::span(vector_span);

  //============================================================================
  // Fill
  std::fill(static_span.begin(), static_span.end(), 0.2F);
  std::fill(dynamic_span.begin(), dynamic_span.end(), -0.2F);
  for (auto& span : sspan_sspan) {
    std::fill(span.begin(), span.end(), 0.3F);
  }
  for (auto& span : span_span) {
    std::fill(span.begin(), span.end(), -0.3F);
  }

  // Fill with std::sin
  auto step  = 2.F * 3.14F / kBlockSize * 16;
  auto phase = 0.F;
  for (auto i = 0; i < kBlockSize; ++i) {
    auto val            = std::sin(phase);
    array[i]            = -val;
    vector[i]           = val;
    array_array[0][i]   = val * 1.5F;
    vector_vector[1][i] = -val * 1.5F;
    phase += step;
    if (i % 8 == 0)
      step *= 1.01F;
  }

  // Apply 0.5 gain
  for (auto i = 0; i < kBlockSize; ++i) {
    array[i] *= 0.5F;
    vector[i] *= 0.5F;
    array_array[0][i] *= 0.5F;
    vector_vector[1][i] *= 0.5F;
  }
}