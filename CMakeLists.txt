# start configuration
cmake_minimum_required(VERSION 2.8.12)
project(triqs_cthyb CXX)

# Default to Release build type
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Type of build" FORCE)
endif()
message( STATUS "-------- BUILD-TYPE: ${CMAKE_BUILD_TYPE} -------------")

# Options for the compilation ...
option(Hybridisation_is_complex "If ON, the hybridization Delta(tau) is complex" OFF)
option(Local_hamiltonian_is_complex "If ON, the H_loc is complex" OFF)
option(MeasureG2 "Measure the two particle object (requires the NFFT library)" ON)

# check that options are compatible
if(Hybridisation_is_complex AND NOT Local_hamiltonian_is_complex)
 message(FATAL_ERROR "Combination of options Hybridisation_is_complex=ON "
                     "and Local_hamiltonian_is_complex=OFF is not supported.")
endif()

# Use shared libraries
set(BUILD_SHARED_LIBS ON)

# Load TRIQS and Cpp2Py
find_package(TRIQS 2.1 REQUIRED)
find_package(Cpp2Py 1.6 REQUIRED)

# 2-particle GF measurement requires NFFT
if(MeasureG2)
 find_package(NFFT REQUIRED)
endif()

# Default Install directory to TRIQS_ROOT if not given. Checks an absolute name is given.
if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT OR (NOT IS_ABSOLUTE ${CMAKE_INSTALL_PREFIX}))
  message(STATUS " No install prefix given (or invalid). Defaulting to TRIQS_ROOT")
  set(CMAKE_INSTALL_PREFIX ${TRIQS_ROOT} CACHE PATH "default install path" FORCE)
endif()
message(STATUS "-------- CMAKE_INSTALL_PREFIX: ${CMAKE_INSTALL_PREFIX} -------------")

# Define the TRIQS Version Numbers
set(CTHYB_VERSION_MAJOR 2)
set(CTHYB_VERSION_MINOR 1)
set(CTHYB_VERSION_PATCH 0)
set(CTHYB_VERSION ${CTHYB_VERSION_MAJOR}.${CTHYB_VERSION_MINOR}.${CTHYB_VERSION_PATCH})

triqs_get_git_hash_of_source_dir(CTHYB_GIT_HASH)
MESSAGE(STATUS "Cthyb version : ${CTHYB_VERSION}")
message(STATUS "Git hash: ${CTHYB_GIT_HASH}")

option(Build_Tests "Enable Tests" ON)
option(Build_Documentation "Build documentation" OFF)

# All PRIVATE common options.
# The std for all targets
add_compile_options(-std=c++17)

# Common to all targets (ctint, python, tests).
include_directories(c++)

# To be fixed!!
triqs_set_rpath_for_all_targets()

add_subdirectory(c++/triqs_cthyb)

# Tests
if (${Build_Tests})
 enable_testing()
 add_subdirectory(test)
endif()

if (${TRIQS_WITH_PYTHON_SUPPORT})

 # Python interface
 add_subdirectory(python/triqs_cthyb)

 # Build the documentation
 if (${Build_Documentation})
   add_subdirectory(doc)
 endif()

endif()

option(BUILD_DEBIAN_PACKAGE "Build a deb package" OFF)
if(BUILD_DEBIAN_PACKAGE)
  if(NOT CMAKE_INSTALL_PREFIX STREQUAL "/usr")
    message(FATAL_ERROR "CMAKE_INSTALL_PREFIX must be /usr for packaging")
  endif()
  SET(CPACK_GENERATOR "DEB")
  SET(CPACK_PACKAGE_VERSION ${CTHYB_VERSION})
  SET(CPACK_PACKAGE_CONTACT "https://github.com/TRIQS/cthyb")
  EXECUTE_PROCESS(COMMAND dpkg --print-architecture OUTPUT_VARIABLE CMAKE_DEBIAN_PACKAGE_ARCHITECTURE OUTPUT_STRIP_TRAILING_WHITESPACE)
  SET(CPACK_DEBIAN_PACKAGE_DEPENDS "triqs (>= 2.1)")
  SET(CPACK_DEBIAN_PACKAGE_CONFLICTS "cthyb")
  SET(CPACK_DEBIAN_PACKAGE_SHLIBDEPS ON)
  SET(CPACK_DEBIAN_PACKAGE_GENERATE_SHLIBS ON)
  INCLUDE(CPack)
endif()

#--------------------------------------------------------
#   Remind the user how to set up his/her variables
#--------------------------------------------------------

# Configure and install the file to source to setup the environment variables 
configure_file(${CMAKE_CURRENT_SOURCE_DIR}/cthybvars.sh.in ${CMAKE_CURRENT_BINARY_DIR}/cthybvars.sh @ONLY)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/cthybvars.sh DESTINATION  ${CMAKE_INSTALL_PREFIX}/share)

MESSAGE(STATUS "***************************************************************")
MESSAGE(STATUS "* Use :                                                        ")
MESSAGE(STATUS "*   source ${CMAKE_INSTALL_PREFIX}/share/cthybvars.sh          ")
MESSAGE(STATUS "*                                                              ") 
MESSAGE(STATUS "*   to set up the environment variables                        ") 
MESSAGE(STATUS "***************************************************************")
