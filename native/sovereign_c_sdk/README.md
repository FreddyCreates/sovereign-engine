# Sovereign OS C/C++ SDK

A native, polished, and professional C++ interface for the Sovereign Intelligence Platform. This SDK communicates with the FastAPI backend over REST, enabling zero-latency integrations from native C++ codebases.

## Requirements
- CMake (3.14+)
- C++17 Compiler (GCC, Clang, MSVC)
- libcurl (Must be installed on the system)

## Building the SDK and CLI

```bash
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

This will automatically fetch `nlohmann/json`, link against `libcurl`, and produce two artifacts:
1. `sovereign_sdk` (Static/Shared Library)
2. `sovereign-cli` (Command Line Interface)

## Usage

### Using the CLI
Run the executable to communicate with your backend running on `localhost:8888`.

```bash
# Check system health
./sovereign-cli health

# List available character agents
./sovereign-cli agents

# Dispatch a task to an agent
./sovereign-cli dispatch AXIOM "Analyze the latest capability patterns"
```

### Using the Library in C++
```cpp
#include <sovereign_sdk.hpp>
#include <iostream>

int main() {
    // Initializes connection to localhost:8888 by default
    sovereign::SovereignClient client;
    
    try {
        auto health = client.get_health();
        std::cout << "Phi Score: " << health["phi"] << "\n";
    } catch (const sovereign::ApiException& e) {
        std::cerr << "Error: " << e.what() << "\n";
    }
    
    return 0;
}
```
