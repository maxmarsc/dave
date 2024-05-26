add_executable(std
    ${CMAKE_CURRENT_SOURCE_DIR}/std.cpp
)

set_target_properties(std PROPERTIES CXX_STANDARD 20)


add_executable(c_example
    ${CMAKE_CURRENT_SOURCE_DIR}/c_example.c
)
