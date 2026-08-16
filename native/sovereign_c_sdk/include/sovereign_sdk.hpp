#ifndef SOVEREIGN_SDK_HPP
#define SOVEREIGN_SDK_HPP

#include <string>
#include <vector>
#include <map>
#include <stdexcept>
#include <nlohmann/json.hpp>

namespace sovereign {

    // Custom Exception Class for API Errors
    class ApiException : public std::runtime_error {
    public:
        explicit ApiException(const std::string& message) : std::runtime_error(message) {}
    };

    // Main SDK Client Class
    class SovereignClient {
    public:
        // Initialize client with the backend URL (default is localhost:8888)
        explicit SovereignClient(const std::string& base_url = "http://127.0.0.1:8888");
        ~SovereignClient();

        // System Health
        nlohmann::json get_health();

        // Agents API
        nlohmann::json get_agents();
        nlohmann::json dispatch_task(const std::string& agent_name, const std::string& prompt, const std::string& priority = "NORMAL");

        // Capabilities API
        nlohmann::json get_capabilities();
        nlohmann::json run_capability(const std::string& capability_id, const std::map<std::string, nlohmann::json>& kwargs);

        // Protocols API
        nlohmann::json get_protocols();

    private:
        std::string base_url_;

        // Helper function for making HTTP GET requests
        std::string http_get(const std::string& endpoint);

        // Helper function for making HTTP POST requests
        std::string http_post(const std::string& endpoint, const std::string& payload);
    };

} // namespace sovereign

#endif // SOVEREIGN_SDK_HPP
