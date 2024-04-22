cmake_minimum_required(VERSION 3.16.3)
PROJECT(test)

AUX_SOURCE_DIRECTORY(src DIR_SRCS)

SET(TEST_MATH ${DIR_SRCS})
ADD_EXECUTABLE(${PROJECT_NAME} ${TEST_MATH})
add_executable (foo ./src/test.cpp)
set(Glog_DIR "/usr/lib/x86_64-linux-gnu/")
add_compile_options(-std=c++11)
set(CMAKE_BUILD_TYPE Release)
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)

# link_libraries()
find_package (GFlags REQUIRED)
message(STATUS "GLOG_INCLUDE_DIRS: ${GLOG_LIBRARIES}")
# find_package(Glog REQUIRED)

# target_link_libraries (foo ) #${GLOG_LIBRARIES}
