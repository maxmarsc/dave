#include <array>
#include <cmath>
#include <complex>

#include <juce_dsp/juce_dsp.h>

#include "numerics.hpp"

constexpr auto kBlockSize = 3;
// constexpr auto kChannels  = 2;
// constexpr auto kSampleRate = 44100.0;
// constexpr auto kCutoff     = 6000.F;
// constexpr auto kQ          = 0.7F;

static void audioBufferMono() {
  /// audioBufferMono::0
  auto buffer_f_data  = std::array<std::array<float, kBlockSize>, 1>{};
  auto buffer_f_p_arr = std::array<float*, 1>{buffer_f_data[0].data()};
  auto buffer_d_data  = std::array<std::array<double, kBlockSize>, 1>{};
  auto buffer_d_p_arr = std::array<double*, 1>{buffer_d_data[0].data()};

  auto buffer_f   = juce::AudioBuffer<float>(1, kBlockSize);
  auto buffer_f_p = juce::AudioBuffer(buffer_f_p_arr.data(), 1, kBlockSize);
  auto buffer_d   = juce::AudioBuffer<double>(1, kBlockSize);
  auto buffer_d_p = juce::AudioBuffer(buffer_d_p_arr.data(), 1, kBlockSize);

  /// audioBufferMono::1
  buffer_f.getWritePointer(0)[0]   = 1.F;
  buffer_f_p.getWritePointer(0)[0] = 1.F;
  buffer_d.getWritePointer(0)[0]   = 1.F;
  buffer_d_p.getWritePointer(0)[0] = 1.F;
  buffer_f.getWritePointer(0)[1]   = -1.F;
  buffer_f_p.getWritePointer(0)[1] = -1.F;
  buffer_d.getWritePointer(0)[1]   = -1.F;
  buffer_d_p.getWritePointer(0)[1] = -1.F;
  /// audioBufferMono::2
}

int main() {
  audioBufferMono();

  return 0;
}