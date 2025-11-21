#define HART_IMPLEMENTATION
#include "hart.hpp"

HART_DECLARE_ALIASES_FOR_FLOAT;
using AudioBuffer = hart::AudioBuffer<float>;
using hart::roundToSizeT;

int main()
{
    constexpr double sampleRateHz = 44100.0;

    // Sine sweep
    const size_t sineSweepDurationFrames = roundToSizeT (sampleRateHz * 1.0_s);
    AudioBuffer bufferA (1, sineSweepDurationFrames);
    auto sineSweepSignalA = SineSweep();
    sineSweepSignalA.prepare (
        sampleRateHz,
        1,  // numOutputChannels
        sineSweepDurationFrames  // maxBlockSizeFrames
        );
    sineSweepSignalA.renderNextBlock (bufferA);

    // A different sweep, overwrites the same buffer
    auto sineSweepSignalB = SineSweep()
        .withType (SineSweep::SweepType::linear)
        .withStartFrequency (100_Hz)
        .withEndFrequency (1_Hz)
        .withDuration (500_ms)
        .withLoop (SineSweep::Loop::yes);
    sineSweepSignalB.prepare (
        sampleRateHz,
        1,  // numOutputChannels
        sineSweepDurationFrames  // maxBlockSizeFrames
        );
    sineSweepSignalB.renderNextBlock (bufferA);

    // Multi-channel noise
    constexpr size_t multiChannelNoiseNumChannels = 5;
    const size_t multiChannelNoiseDurationFrames = hart::roundToSizeT (sampleRateHz * 10_ms);
    AudioBuffer bufferB (multiChannelNoiseNumChannels, multiChannelNoiseDurationFrames);
    auto multiChannelNoiseSignal = WhiteNoise();
    multiChannelNoiseSignal.prepare (
        sampleRateHz,
        multiChannelNoiseNumChannels,  // numOutputChannels
        multiChannelNoiseDurationFrames  // maxBlockSizeFrames
        );
    multiChannelNoiseSignal.renderNextBlock (bufferB);
    multiChannelNoiseSignal.renderNextBlock (bufferB);  // Some more noise...
    multiChannelNoiseSignal.renderNextBlock (bufferB);  // ...and more noise

    return 0;
}
