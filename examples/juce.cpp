#include <juce_dsp/juce_dsp.h>
#include <array>
#include <cmath>
#include <complex>

constexpr auto kBlockSize  = 256;
constexpr auto kChannels   = 2;
constexpr auto kSampleRate = 44100.0;
constexpr auto kCutoff     = 6000.F;
constexpr auto kQ          = 0.7F;

int main() {
  //============================================================================
  auto audio_buffer_data =
      std::array<std::array<float, kBlockSize>, kChannels>{};
  auto audio_buffer_p_arr = std::array<float*, kChannels>{
      audio_buffer_data[0].data(), audio_buffer_data[1].data()};

  auto audio_buffer   = juce::AudioBuffer<float>(kChannels, kBlockSize);
  auto audio_buffer_p = juce::AudioBuffer<float>(audio_buffer_p_arr.data(),
                                                 kChannels, kBlockSize);

  //============================================================================
  auto audio_block_data =
      std::array<std::array<float, kBlockSize>, kChannels>{};
  auto audio_block_p_arr = std::array<float*, kChannels>{
      audio_block_data[0].data(), audio_block_data[1].data()};

  auto audio_block = juce::dsp::AudioBlock<float>(audio_block_p_arr.data(),
                                                  kChannels, kBlockSize);

  //============================================================================
  auto lp_so_coeffs = juce::dsp::IIR::Coefficients<float>::makeLowPass(
      kSampleRate, kCutoff, kQ);
  auto& lp_so_coeffs_r = *lp_so_coeffs.get();
  auto lp_fo_coeffs =
      juce::dsp::IIR::Coefficients<float>::makeFirstOrderLowPass(kSampleRate,
                                                                 kCutoff);
  auto& lp_fo_coeffs_r = *lp_fo_coeffs.get();
  auto lp_so_filter    = juce::dsp::IIR::Filter<float>(lp_so_coeffs);
  auto lp_fo_filter    = juce::dsp::IIR::Filter<float>(lp_fo_coeffs);

  // Create the filter and set its coefficients
  juce::dsp::IIR::Filter<float> filter;
  filter.coefficients = lp_so_coeffs;

  // Prepare the filter with processing specifications
  juce::dsp::ProcessSpec spec{};
  spec.sampleRate       = kSampleRate;
  spec.maximumBlockSize = kBlockSize;
  spec.numChannels      = kChannels;
  filter.prepare(spec);

  //============================================================================
  auto old_svf_filter  = juce::dsp::StateVariableFilter::Filter<float>();
  auto& old_svf_coeffs = *old_svf_filter.parameters;
  old_svf_filter.parameters->setCutOffFrequency(kSampleRate, kCutoff);
  old_svf_filter.parameters->type =
      juce::dsp::StateVariableFilter::StateVariableFilterType::lowPass;

  //============================================================================
  // Fill with values
  audio_block.fill(1.F);
  for (auto& arr : audio_buffer_data) {
    arr.fill(2.F);
  }
  std::fill(audio_buffer.getWritePointer(0),
            audio_buffer.getWritePointer(0) + kBlockSize, 2.5F);

  // Fill with std::sin
  auto step  = 2.F * 3.14F / kBlockSize * 16;
  auto phase = 0.F;
  for (auto i = 0; i < kBlockSize; ++i) {
    auto val = std::sin(phase);

    audio_block.setSample(0, i, val);
    audio_block.setSample(1, i, val / 2.F);
    audio_buffer.getWritePointer(0)[i]   = -val;
    audio_buffer.getWritePointer(1)[i]   = -val / 2.F;
    audio_buffer_p.getWritePointer(0)[i] = -val;
    audio_buffer_p.getWritePointer(1)[i] = -val / 2.F;

    if (i % 8 == 0)
      step *= 1.01F;
    phase += step;
  }

  //============================================================================
  // Update the SVF filters
  old_svf_filter.parameters->type =
      juce::dsp::StateVariableFilter::StateVariableFilterType::bandPass;

  //============================================================================
  // Process with the filter
  juce::dsp::ProcessContextReplacing<float> context(audio_block);

  //============================================================================
  // Update the SVF filters
  old_svf_filter.parameters->type =
      juce::dsp::StateVariableFilter::StateVariableFilterType::highPass;

  //============================================================================
  return 0;
}