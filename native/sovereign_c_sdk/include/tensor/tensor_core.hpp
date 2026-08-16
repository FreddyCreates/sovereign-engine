// [SOVEREIGN FORGE] Algorithmic C++ Synthesis
// Namespace: sovereign::tensor | Class: TensorCore

#include <vector>
#include <stdexcept>
#include <iostream>
#include <memory>

namespace sovereign::tensor {

class TensorCore {
public:
    void TensorCore(std::vector<int> shape) {
        this->shape = shape;
int total_size = 1;
for(int dim : shape) total_size *= dim;
data = std::vector<float>(total_size, 0.0f);
    }

    int get_size() {
        return data.size();
    }


};

} // namespace sovereign::tensor
