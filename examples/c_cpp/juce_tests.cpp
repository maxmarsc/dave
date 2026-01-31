#include <array>
#include <cmath>
#include <complex>

#include <juce_dsp/juce_dsp.h>

#include "numerics.hpp"

#pragma clang diagnostic ignored "-Wdeprecated-declarations"

constexpr auto kBlockSize = 3;

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

  buffer_f.clear();
  buffer_f_p.clear();
  buffer_d.clear();
  buffer_d_p.clear();

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

static void audioBufferMultiChannel() {
  /// audioBufferMultiChannel::0
  constexpr auto kChannels = 2;
  auto buffer_f_data =
      std::array<std::array<float, kBlockSize * kChannels>, kChannels>{};
  auto buffer_f_p_arr = std::array<float*, kChannels>{buffer_f_data[0].data(),
                                                      buffer_f_data[1].data()};
  auto buffer_d_data =
      std::array<std::array<double, kBlockSize * kChannels>, kChannels>{};
  auto buffer_d_p_arr = std::array<double*, kChannels>{buffer_d_data[0].data(),
                                                       buffer_d_data[1].data()};

  auto buffer_f = juce::AudioBuffer<float>(kChannels, kBlockSize);
  auto buffer_f_p =
      juce::AudioBuffer(buffer_f_p_arr.data(), kChannels, kBlockSize);
  auto buffer_d = juce::AudioBuffer<double>(kChannels, kBlockSize);
  auto buffer_d_p =
      juce::AudioBuffer(buffer_d_p_arr.data(), kChannels, kBlockSize);

  buffer_f.clear();
  buffer_f_p.clear();
  buffer_d.clear();
  buffer_d_p.clear();

  /// audioBufferMultiChannel::1
  buffer_f.getWritePointer(1)[0]   = 1.F;
  buffer_f_p.getWritePointer(1)[0] = 1.F;
  buffer_d.getWritePointer(1)[0]   = 1.F;
  buffer_d_p.getWritePointer(1)[0] = 1.F;
  buffer_f.getWritePointer(1)[1]   = -1.F;
  buffer_f_p.getWritePointer(1)[1] = -1.F;
  buffer_d.getWritePointer(1)[1]   = -1.F;
  buffer_d_p.getWritePointer(1)[1] = -1.F;
  /// audioBufferMultiChannel::2
}

static void audioBlock() {
  /// audioBlock::0
  constexpr auto kChannels = 2;
  auto block_f_data  = std::array<std::array<float, kBlockSize>, kChannels>{};
  auto block_f_p_arr = std::array<float*, kChannels>{block_f_data[0].data(),
                                                     block_f_data[1].data()};
  auto block_d_data  = std::array<std::array<double, kBlockSize>, kChannels>{};
  auto block_d_p_arr = std::array<double*, kChannels>{block_d_data[0].data(),
                                                      block_d_data[1].data()};

  auto block_f =
      juce::dsp::AudioBlock<float>(block_f_p_arr.data(), kChannels, kBlockSize);
  auto block_d = juce::dsp::AudioBlock<double>(block_d_p_arr.data(), kChannels,
                                               kBlockSize);

  /// audioBlock::1
  block_f.getChannelPointer(1)[0] = 1.F;
  block_d.getChannelPointer(1)[0] = 1.F;
  block_f.getChannelPointer(1)[1] = -1.F;
  block_d.getChannelPointer(1)[1] = -1.F;
  /// audioBlock::2
}

static void iirSOS() {
  /// iirSOS::0
  constexpr auto kChannels   = 1;
  constexpr auto kSampleRate = 44100.0;
  constexpr auto kCutoff     = 6000.F;
  constexpr auto kQ          = 0.7F;
  constexpr auto kSpec =
      juce::dsp::ProcessSpec{kSampleRate, kBlockSize, kChannels};

  auto coeffs_f_fo_rc =
      juce::dsp::IIR::Coefficients<float>::makeFirstOrderLowPass(kSampleRate,
                                                                 kCutoff);
  auto coeffs_d_fo_rc =
      juce::dsp::IIR::Coefficients<double>::makeFirstOrderLowPass(kSampleRate,
                                                                  kCutoff);
  auto coeffs_f_so_rc = juce::dsp::IIR::Coefficients<float>::makeLowPass(
      kSampleRate, kCutoff, kQ);
  auto coeffs_d_so_rc = juce::dsp::IIR::Coefficients<double>::makeLowPass(
      kSampleRate, kCutoff, kQ);
  [[maybe_unused]] auto& coeffs_f_fo = *coeffs_f_fo_rc.get();
  [[maybe_unused]] auto& coeffs_d_fo = *coeffs_d_fo_rc.get();
  [[maybe_unused]] auto& coeffs_f_so = *coeffs_f_so_rc.get();
  [[maybe_unused]] auto& coeffs_d_so = *coeffs_d_so_rc.get();
  auto filter_f_fo = juce::dsp::IIR::Filter<float>(coeffs_f_fo_rc);
  auto filter_d_fo = juce::dsp::IIR::Filter<double>(coeffs_d_fo_rc);
  auto filter_f_so = juce::dsp::IIR::Filter<float>(coeffs_f_so_rc);
  auto filter_d_so = juce::dsp::IIR::Filter<double>(coeffs_d_so_rc);
  filter_f_fo.prepare(kSpec);
  filter_d_fo.prepare(kSpec);
  filter_f_so.prepare(kSpec);
  filter_d_so.prepare(kSpec);
  /// iirSOS::1
}

static void iirSVF() {
  /// iirSVF::0
  constexpr auto kChannels   = 1;
  constexpr auto kSampleRate = 44100.0;
  constexpr auto kCutoff     = 6000.F;
  constexpr auto kSpec =
      juce::dsp::ProcessSpec{kSampleRate, kBlockSize, kChannels};

  auto old_filter_f = juce::dsp::StateVariableFilter::Filter<float>();
  auto old_filter_d = juce::dsp::StateVariableFilter::Filter<double>();
  auto filter_f     = juce::dsp::StateVariableTPTFilter<float>();
  auto filter_d     = juce::dsp::StateVariableTPTFilter<double>();
  old_filter_f.parameters->setCutOffFrequency(kSampleRate, kCutoff);
  old_filter_f.parameters->type =
      juce::dsp::StateVariableFilter::StateVariableFilterType::lowPass;
  old_filter_d.parameters->setCutOffFrequency(kSampleRate, kCutoff);
  old_filter_d.parameters->type =
      juce::dsp::StateVariableFilter::StateVariableFilterType::lowPass;
  filter_f.setType(juce::dsp::StateVariableTPTFilter<float>::Type::lowpass);
  filter_d.setType(juce::dsp::StateVariableTPTFilter<double>::Type::lowpass);
  old_filter_f.prepare(kSpec);
  old_filter_d.prepare(kSpec);
  filter_f.prepare(kSpec);
  filter_d.prepare(kSpec);
  /// iirSVF::1
  old_filter_f.parameters->type =
      juce::dsp::StateVariableFilter::StateVariableFilterType::bandPass;
  old_filter_d.parameters->type =
      juce::dsp::StateVariableFilter::StateVariableFilterType::bandPass;
  filter_f.setType(juce::dsp::StateVariableTPTFilter<float>::Type::bandpass);
  filter_d.setType(juce::dsp::StateVariableTPTFilter<double>::Type::bandpass);
  /// iirSVF::2
  old_filter_f.parameters->type =
      juce::dsp::StateVariableFilter::StateVariableFilterType::highPass;
  old_filter_d.parameters->type =
      juce::dsp::StateVariableFilter::StateVariableFilterType::highPass;
  filter_f.setType(juce::dsp::StateVariableTPTFilter<float>::Type::highpass);
  filter_d.setType(juce::dsp::StateVariableTPTFilter<double>::Type::highpass);
  /// iirSVF::3
}

int main() {
  audioBufferMono();
  audioBufferMultiChannel();
  audioBlock();
  iirSOS();
  iirSVF();

  return 0;
}