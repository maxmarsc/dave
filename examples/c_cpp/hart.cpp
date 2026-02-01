#define HART_IMPLEMENTATION
#include "hart.hpp"

// NOLINTNEXTLINE(google-build-using-namespace)
HART_DECLARE_ALIASES_FOR_FLOAT;
using AudioBuffer = hart::AudioBuffer<float>;
using hart::roundToSizeT;

int main() {
  constexpr double kSampleRateHz = 44100.0;

  // Sine sweep
  const size_t sine_sweep_duration_frames = roundToSizeT(kSampleRateHz * 1.0_s);
  AudioBuffer buffer_a(1, sine_sweep_duration_frames);
  auto sine_sweep_signal_a = SineSweep();
  sine_sweep_signal_a.prepare(kSampleRateHz,
                              1,                          // numOutputChannels
                              sine_sweep_duration_frames  // maxBlockSizeFrames
  );
  sine_sweep_signal_a.renderNextBlock(buffer_a);

  // A different sweep, overwrites the same buffer
  auto sine_sweep_signal_b = SineSweep()
                                 .withType(SineSweep::SweepType::linear)
                                 .withStartFrequency(100_Hz)
                                 .withEndFrequency(1_Hz)
                                 .withDuration(500_ms)
                                 .withLoop(SineSweep::Loop::yes);
  sine_sweep_signal_b.prepare(kSampleRateHz,
                              1,                          // numOutputChannels
                              sine_sweep_duration_frames  // maxBlockSizeFrames
  );
  sine_sweep_signal_b.renderNextBlock(buffer_a);

  // Multi-channel noise
  constexpr size_t kMultiChannelNoiseNumChannels = 5;
  const size_t multi_channel_noise_duration_frames =
      hart::roundToSizeT(kSampleRateHz * 10_ms);
  AudioBuffer buffer_b(kMultiChannelNoiseNumChannels,
                       multi_channel_noise_duration_frames);
  auto multi_channel_noise_signal = WhiteNoise();
  multi_channel_noise_signal.prepare(
      kSampleRateHz,
      kMultiChannelNoiseNumChannels,       // numOutputChannels
      multi_channel_noise_duration_frames  // maxBlockSizeFrames
  );
  multi_channel_noise_signal.renderNextBlock(buffer_b);
  multi_channel_noise_signal.renderNextBlock(buffer_b);  // Some more noise...
  multi_channel_noise_signal.renderNextBlock(buffer_b);  // ...and more noise

  return 0;
}
