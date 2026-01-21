#include <cmath>
#include <vector>

#pragma once

// examples of a custom structure
template <typename T>
struct DaveCustomContainerPtr final {
  T* ptr_;
  int size_;
};

struct DaveCustomContainerPtrPtr {
  float** ptr_;
  int block_size_;
  int channels_;
};

struct DaveCustomInterleavedContainerVec {
  std::vector<float> vec_;
  int block_size_;
  int channels_;
};

struct DaveCustomContainerVecRef {
  std::vector<float>& vec_ref_;
  int block_size_;
  int channels_;
};