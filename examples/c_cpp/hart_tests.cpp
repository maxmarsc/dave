#define HART_IMPLEMENTATION
#include "hart_audio_buffer.hpp"

#include "test_utils.hpp"

/**
 * @brief File used to unit test the server-side features of DAVE
 * @warning BE CAREFUL WHEN EDITING THIS FILE
 * 
 * @details The tests uses automatic parsing of the source code to identify
 * "tags" ie: //// <tag>::<index>
 * A tag is used to indicate a relevant location to place a breakpoint.
 */

static void audioBuffer() {
  //// audioBuffer::0
  constexpr auto kNumChannels = 2;
  constexpr auto kNumFrames   = 3;

  auto buffer_f = hart::AudioBuffer<float>(kNumChannels, kNumFrames);
  auto buffer_d = hart::AudioBuffer<double>(kNumChannels, kNumFrames);
  //// audioBuffer::1
  buffer_f.getArrayOfWritePointers()[1][0] = 1.F;
  buffer_d.getArrayOfWritePointers()[1][0] = 1.;
  buffer_f.getArrayOfWritePointers()[1][1] = -1.F;
  buffer_d.getArrayOfWritePointers()[1][1] = -1.;
  //// audioBuffer::2
  BREAKABLE_END;
}

int main() {
  audioBuffer();
  return 0;
}