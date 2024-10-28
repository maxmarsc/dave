#include <array>
#include <cmath>
#include <complex>
#include "choc/audio/choc_SampleBuffers.h"

constexpr auto kBlockSize = 4096;
constexpr auto kChannels  = 2;

int main() {
  //============================================================================
  auto mono_buffer = choc::buffer::MonoBuffer<float>(1, kBlockSize);
  auto stereo_buffer =
      choc::buffer::ChannelArrayBuffer<float>(kChannels, kBlockSize);
  auto interleaved_buffer =
      choc::buffer::InterleavedBuffer<float>(kChannels, kBlockSize);

  //============================================================================
  auto mono_view        = mono_buffer.getView();
  auto stereo_view      = stereo_buffer.getView();
  auto interleaved_view = interleaved_buffer.getView();

  //============================================================================
  // Fill with values
  for (auto i = 0; i < kBlockSize; ++i) {
    mono_view.getSample(0, i)        = 1.F;
    stereo_view.getSample(0, i)      = 0.5F;
    stereo_view.getSample(1, i)      = -0.5F;
    interleaved_view.getSample(0, i) = 0.5F;
    interleaved_view.getSample(1, i) = -0.5F;
  }

  // Fill with std::sin
  auto step  = 2.F * 3.14F / kBlockSize * 16;
  auto phase = 0.F;
  for (auto i = 0; i < kBlockSize; ++i) {
    auto val = std::sin(phase);

    mono_view.getSample(0, i)        = val;
    stereo_view.getSample(0, i)      = -val;
    stereo_view.getSample(1, i)      = val / 2.F;
    interleaved_view.getSample(0, i) = -val / 2.F;
    interleaved_view.getSample(1, i) = val * val;

    if (i % 8 == 0)
      step *= 1.01F;
    phase += step;
  }

  return 0;
}