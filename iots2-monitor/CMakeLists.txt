cmake_minimum_required(VERSION 3.5)

project(iots2-monitor LANGUAGES CXX)

set_target_properties(
    PROPERTIES
    CXX_STANDARD 17
    CXX_EXTENSIONS OFF
    CXX_STANDARD_REQUIRED ON
    POSITION_INDEPENDENT_CODE 1
    )

set_target_properties(
    PROPERTIES
 	CXX_STANDARD 17
 	CXX_EXTENSIONS OFF
 	CXX_STANDARD_REQUIRED ON
)

add_executable(iots2-monitor main.cpp Helper.hpp tcp_client.hpp)
