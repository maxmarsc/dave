#include <complex>

#pragma once

constexpr auto kCpxZeroF     = std::complex<float>(0.F, 0.F);
constexpr auto kCpxZeroD     = std::complex<double>(0., 0.);
constexpr auto kCpxOneF      = std::complex<float>(1.F, 1.F);
constexpr auto kCpxOneD      = std::complex<double>(1., 1.);
constexpr auto kCpxMinusOneF = std::complex<float>(-1.F, -1.F);
constexpr auto kCpxMinusOneD = std::complex<double>(-1., -1.);
constexpr auto kNanF         = std::numeric_limits<float>::quiet_NaN();
constexpr auto kPInfF        = std::numeric_limits<float>::infinity();
constexpr auto kNInfF        = -std::numeric_limits<float>::infinity();
constexpr auto kNanD         = std::numeric_limits<double>::quiet_NaN();
constexpr auto kPInfD        = std::numeric_limits<double>::infinity();
constexpr auto kNInfD        = -std::numeric_limits<double>::infinity();