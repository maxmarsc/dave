#include <complex.h>
#include <math.h>
#include <stdlib.h>

static const int kBlock_Size = 4096;

void complexFunction() {
}

float frand() {
  float mid = (float)RAND_MAX / 2.F;
  return ((float)rand() - mid) / mid;
}

double drand() {
  float mid = (float)RAND_MAX / 2.F;
  return ((float)rand() - mid) / mid;
}

int main() {
  // Syntax 1
  {
    float real_f_carray[kBlock_Size];
    complex float cpx_f_carray[kBlock_Size];
    double real_d_carray[kBlock_Size];
    complex double cpx_d_carray[kBlock_Size];

    // Fill with random
    for (int i=0; i<kBlock_Size; ++i) {
      real_f_carray[i] = frand();
      cpx_f_carray[i] = frand() + I * frand();
      real_d_carray[i] = drand();
      cpx_d_carray[i] = drand() + I * drand();
    }

    // Apply 0.5 gain
    for (int i=0; i<kBlock_Size; ++i) {
      real_f_carray[i] *= 0.5F;
      cpx_f_carray[i] *= 0.5F;
      real_d_carray[i] *= 0.5;
      cpx_d_carray[i] *= 0.5;
    }
  }

  // Syntax 2
  {
    float real_f_carray[kBlock_Size];
    float _Complex cpx_f_carray[kBlock_Size];
    double real_d_carray[kBlock_Size];
    double _Complex cpx_d_carray[kBlock_Size];

    // Fill with random
    for (int i=0; i<kBlock_Size; ++i) {
      real_f_carray[i] = frand();
      cpx_f_carray[i] = frand() + I * frand();
      real_d_carray[i] = drand();
      cpx_d_carray[i] = drand() + I * drand();
    }

    // Apply 0.5 gain
    for (int i=0; i<kBlock_Size; ++i) {
      real_f_carray[i] *= 0.5F;
      cpx_f_carray[i] *= 0.5F;
      real_d_carray[i] *= 0.5;
      cpx_d_carray[i] *= 0.5;
    }

  }


  // real
  // complexFunction();
  return 0;
}
