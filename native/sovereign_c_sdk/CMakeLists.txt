cmake_minimum_required(VERSION 3.14)
project(SovereignSDK VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# We will use FetchContent to easily grab nlohmann/json
include(FetchContent)

FetchContent_Declare(json
  URL https://github.com/nlohmann/json/releases/download/v3.11.3/json.tar.xz
)
FetchContent_MakeAvailable(json)

# Find LibCURL (required for HTTP)
# Make sure libcurl is installed on the system
find_package(CURL REQUIRED)

# Include directories
include_directories(include)

# Create the Library
add_library(sovereign_sdk src/sovereign_sdk.cpp)
target_link_libraries(sovereign_sdk PUBLIC CURL::libcurl nlohmann_json::nlohmann_json)
target_include_directories(sovereign_sdk PUBLIC include)

# Create the CLI Executable
add_executable(sovereign-cli src/cli_main.cpp)
target_link_libraries(sovereign-cli PRIVATE sovereign_sdk)

# Create the Supercomputer Node Executable
add_executable(supercomputer-node src/supercomputer_node.cpp)
target_link_libraries(supercomputer-node PRIVATE sovereign_sdk)

# Installation rules
install(TARGETS sovereign_sdk sovereign-cli supercomputer-node
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib)
install(DIRECTORY include/ DESTINATION include)
