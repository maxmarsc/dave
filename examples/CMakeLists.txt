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


add_executable(std
    ${CMAKE_CURRENT_SOURCE_DIR}/std.cpp
)

set_target_properties(std PROPERTIES CXX_STANDARD 20)

add_executable(cpp_scope
    ${CMAKE_CURRENT_SOURCE_DIR}/cpp_scope.cpp
)

set_target_properties(cpp_scope PROPERTIES CXX_STANDARD 20)


add_executable(c_example
    ${CMAKE_CURRENT_SOURCE_DIR}/c_example.c
)


add_executable(juce
    ${CMAKE_CURRENT_SOURCE_DIR}/juce.cpp
)
set_target_properties(juce PROPERTIES CXX_STANDARD 20)
target_link_libraries(
  juce
  PUBLIC juce::juce_recommended_config_flags
         juce::juce_recommended_warning_flags juce::juce_dsp
)
target_compile_definitions(
  juce
  PUBLIC JUCE_USE_CURL=0
)

add_executable(
  gsl
  ${CMAKE_CURRENT_SOURCE_DIR}/gsl.cpp
)
set_target_properties(gsl PROPERTIES CXX_STANDARD 17)

target_link_libraries(gsl PUBLIC Microsoft.GSL::GSL)