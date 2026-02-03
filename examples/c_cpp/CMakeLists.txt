cmake_minimum_required(VERSION 3.16)

project(dave_examples VERSION 0.0.1)

option(DAVE_BUILD_TESTS OFF)
option(DAVE_LINK_LIBCPP OFF)

if(DAVE_LINK_LIBCPP)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -stdlib=libc++")
  set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -stdlib=libc++")
  set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -stdlib=libc++")
endif()

################################################################################
###                             dependencies
################################################################################
include(FetchContent)
set(JUCE_USE_CURL OFF)
FetchContent_Declare(
  juce_project
  GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
  GIT_PROGRESS TRUE
  GIT_SHALLOW TRUE
  GIT_TAG 8.0.1
)
set(JUCE_MODULES_ONLY ON)
FetchContent_MakeAvailable(juce_project)


set(GSL_INSTALL OFF)
set(GSL_TEST OFF)
FetchContent_Declare(
  GSL
  GIT_REPOSITORY "https://github.com/microsoft/GSL"
  GIT_TAG "v4.0.0"
  GIT_SHALLOW ON
)

FetchContent_MakeAvailable(GSL)

FetchContent_Declare(
        choc_project
        GIT_REPOSITORY https://github.com/Tracktion/choc.git
        GIT_TAG 68a63dd73d709ecb45b3fe31c3fa903323ad10fa)
FetchContent_MakeAvailable(choc_project)

set(HART_BUILD_TESTS OFF)
FetchContent_Declare(
  HART
  GIT_REPOSITORY "https://github.com/daleonov/HART.git"
  GIT_TAG 0.1.0
  GIT_SHALLOW ON
)

FetchContent_MakeAvailable(HART)

################################################################################
###                             stdlib
################################################################################
add_executable(std
    ${CMAKE_CURRENT_SOURCE_DIR}/std.cpp
)

set_target_properties(std PROPERTIES CXX_STANDARD 20)

if (DAVE_BUILD_TESTS)
add_executable(std_tests
    ${CMAKE_CURRENT_SOURCE_DIR}/std_tests.cpp
)

set_target_properties(std_tests PROPERTIES CXX_STANDARD 20)
endif()

################################################################################
###                             scope
################################################################################
add_executable(cpp_scope
    ${CMAKE_CURRENT_SOURCE_DIR}/cpp_scope.cpp
)

set_target_properties(cpp_scope PROPERTIES CXX_STANDARD 20)


################################################################################
###                               C
################################################################################
add_executable(c_example
    ${CMAKE_CURRENT_SOURCE_DIR}/c_example.c
)

################################################################################
###                               JUCE
################################################################################
add_executable(juce_example
    ${CMAKE_CURRENT_SOURCE_DIR}/juce.cpp
)
set_target_properties(juce_example PROPERTIES CXX_STANDARD 20)
target_link_libraries(
  juce_example
  PUBLIC juce::juce_recommended_config_flags
         juce::juce_recommended_warning_flags juce::juce_dsp
)
target_compile_definitions(
  juce_example
  PUBLIC JUCE_USE_CURL=0
)
target_compile_options(
  juce_example
  PRIVATE
  -Wno-deprecated-declarations
  -Wno-unknown-pragmas
)

if (DAVE_BUILD_TESTS)
add_executable(juce_tests
    ${CMAKE_CURRENT_SOURCE_DIR}/juce_tests.cpp
)

set_target_properties(juce_tests PROPERTIES CXX_STANDARD 20)
target_link_libraries(
  juce_tests
  PUBLIC juce::juce_recommended_config_flags
         juce::juce_recommended_warning_flags juce::juce_dsp
)
target_compile_definitions(
  juce_tests
  PUBLIC JUCE_USE_CURL=0
)
target_compile_options(
  juce_tests
  PRIVATE
  -Wno-deprecated-declarations
  -Wno-unknown-pragmas
)
endif()

################################################################################
###                               Microsoft's GSL
################################################################################
add_executable(
  gsl
  ${CMAKE_CURRENT_SOURCE_DIR}/gsl.cpp
)
set_target_properties(gsl PROPERTIES CXX_STANDARD 17)

target_link_libraries(gsl PUBLIC Microsoft.GSL::GSL)

if (DAVE_BUILD_TESTS)
add_executable(gsl_tests
    ${CMAKE_CURRENT_SOURCE_DIR}/std_tests.cpp
)

set_target_properties(gsl_tests PROPERTIES CXX_STANDARD 20)
target_link_libraries(gsl_tests PUBLIC Microsoft.GSL::GSL)
target_compile_definitions(gsl_tests PUBLIC USE_GSL)

endif()

################################################################################
###                               CHOC
################################################################################
add_executable(
  choc_example
  ${CMAKE_CURRENT_SOURCE_DIR}/choc.cpp
)
set_target_properties(choc_example PROPERTIES CXX_STANDARD 17)
target_link_libraries(choc_example PUBLIC choc::choc)

################################################################################
###                               HART
################################################################################

add_executable(
  hart
  ${CMAKE_CURRENT_SOURCE_DIR}/hart.cpp
)
set_target_properties(hart PROPERTIES CXX_STANDARD 11)
target_link_libraries(hart PRIVATE HART::HART)

if (DAVE_BUILD_TESTS)
add_executable(
  hart_tests
  ${CMAKE_CURRENT_SOURCE_DIR}/hart_tests.cpp
)
set_target_properties(hart_tests PROPERTIES CXX_STANDARD 11)
target_link_libraries(hart_tests PRIVATE HART::HART)
endif()

################################################################################
###                          Custom containers example
################################################################################
add_executable(
  custom_containers
  ${CMAKE_CURRENT_SOURCE_DIR}/custom_containers.cpp
)
set_target_properties(custom_containers PROPERTIES CXX_STANDARD 20)

if (DAVE_BUILD_TESTS)
add_executable(custom_tests
    ${CMAKE_CURRENT_SOURCE_DIR}/custom_tests.cpp
)

set_target_properties(custom_tests PROPERTIES CXX_STANDARD 20)
endif()