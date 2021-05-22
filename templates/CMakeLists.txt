cmake_minimum_required(VERSION 3.19)
project(@ENTITY_NAME@ VERSION 0.0.1 LANGUAGES CXX)

option(BUILD_SHARED_LIBS "Enable compilation of shared libraries" OFF)
option(ENABLE_CACHE "Enable cache if available" ON)
option(ENABLE_CPPCHECK "Enable testing with cppcheck" TRUE)
option(ENABLE_CLANG_TIDY "Enable testing with clang-tidy" FALSE)
option(WARNINGS_AS_ERRORS "Treat compiler warnings as errors" TRUE)
option(FORCE_COLORED_OUTPUT "Always produce ANSI-colored output (GNU/Clang only)." TRUE)

add_library(project_options INTERFACE)
target_compile_features(project_options INTERFACE cxx_std_17)

add_library(project_warnings INTERFACE)

include(cmake/CompilerWarnings.cmake)
set_warnings(project_warnings)

if (${FORCE_COLORED_OUTPUT})
    if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
        target_compile_options (project_options INTERFACE -fdiagnostics-color=always)
    elseif ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
        target_compile_options (project_options INTERFACE -fcolor-diagnostics)
    endif ()
endif ()

include(cmake/Cache.cmake)
include(cmake/StaticAnalyzers.cmake)

include(cmake/Conan.cmake)
conan_setup()

configure_file(
        "${PROJECT_SOURCE_DIR}/src/include/${PROJECT_NAME}/config.hpp.in"
        "${PROJECT_SOURCE_DIR}/src/include/${PROJECT_NAME}/config.hpp"
)

include_directories("${PROJECT_BINARY_DIR}/include/${PROJECT_NAME}")

message("#########################################")
message("\t \t \t Summary")
message("#########################################")
message("Build type:       \t ${CMAKE_BUILD_TYPE}")
message("Install prefix:   \t ${CMAKE_INSTALL_PREFIX}")
message("Clang-tidy:       \t ${ENABLE_CLANG_TIDY}")
message("Cppcheck:         \t ${ENABLE_CPPCHECK}")
message("Warnings as errors:\t ${WARNINGS_AS_ERRORS}")
message("Compiler:         \t ${CMAKE_CXX_COMPILER_ID}")
message("Shared libs:      \t ${BUILD_SHARED_LIBS}")
message("Cache:            \t ${ENABLE_CACHE}")
message("CCache executable:\t ${CCACHE}")
message("------------------------------------------")
message("Version:          \t ${PROJECT_VERSION}")
message("########################################")

add_subdirectory(src)
add_subdirectory(src/include)