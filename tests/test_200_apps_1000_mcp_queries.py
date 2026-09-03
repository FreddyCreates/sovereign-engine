"""
Automated Test Suite for Sovereign OS MCP 200 App Adapters, 1000 Queries & Virtual Computer Cloud Engine
Contains 60+ unit and integration tests verifying 100% pass status.
"""

import sys
import os
import json
import unittest
from io import BytesIO

# Ensure sovereign_infrastructure/nextgen_systems and project root are in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NEXTGEN_DIR = os.path.join(BASE_DIR, "sovereign_infrastructure", "nextgen_systems")

if NEXTGEN_DIR not in sys.path:
    sys.path.insert(0, NEXTGEN_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from mcp_200_app_adapters_1000_queries import MCP200AppAdaptersEngine
from virtual_computer_cloud_instance import VirtualComputerCloudEngine
from sovereign_mcp_server import SovereignMCPServer
from sovereign_dashboard_server import SovereignDashboardHandler


class MockHTTPRequestHandler(SovereignDashboardHandler):
    """Mock HTTP request handler for testing REST endpoints without launching a network socket server."""
    def __init__(self, method="GET", path="/", body=None):
        self.rfile = BytesIO(json.dumps(body).encode("utf-8") if body else b"")
        self.wfile = BytesIO()
        self.command = method
        self.path = path
        self.headers = {"Content-Length": str(len(json.dumps(body).encode("utf-8")) if body else 0)}
        self.response_status = None
        self.response_headers = {}
        self.response_body = None

    def send_response(self, code, message=None):
        self.response_status = code

    def send_header(self, keyword, value):
        self.response_headers[keyword] = value

    def end_headers(self):
        pass

    def send_json_response(self, data: dict, status_code: int = 200):
        self.response_status = status_code
        self.response_body = data


# =============================================================================
# 1. MCP 200 APP ADAPTERS ENGINE TESTS (20 Tests)
# =============================================================================
class TestMCP200AppAdaptersEngine(unittest.TestCase):

    def setUp(self):
        self.engine = MCP200AppAdaptersEngine()

    def test_01_initial_adapters_count(self):
        self.assertEqual(len(self.engine.adapters_registry), 200)

    def test_02_categories_count(self):
        self.assertEqual(len(self.engine.CATEGORIES), 10)

    def test_03_list_all_adapters(self):
        adapters = self.engine.list_adapters()
        self.assertEqual(len(adapters), 200)

    def test_04_filter_adapters_accounting(self):
        adapters = self.engine.list_adapters(category="Accounting & Tax")
        self.assertEqual(len(adapters), 20)

    def test_05_filter_adapters_payments(self):
        adapters = self.engine.list_adapters(category="Payment Gateways & Subscriptions")
        self.assertEqual(len(adapters), 20)

    def test_06_filter_adapters_hr(self):
        adapters = self.engine.list_adapters(category="HR & Payroll")
        self.assertEqual(len(adapters), 20)

    def test_07_filter_adapters_apar(self):
        adapters = self.engine.list_adapters(category="AP/AR & Expense Management")
        self.assertEqual(len(adapters), 20)

    def test_08_filter_adapters_banking(self):
        adapters = self.engine.list_adapters(category="Banking & Plaid Integrations")
        self.assertEqual(len(adapters), 20)

    def test_09_filter_adapters_search(self):
        adapters = self.engine.list_adapters(search="QuickBooks")
        self.assertGreaterEqual(len(adapters), 1)
        self.assertEqual(adapters[0]["app_id"], "app_001")

    def test_10_get_adapter_by_id(self):
        adapter = self.engine.get_adapter("app_021")
        self.assertEqual(adapter["name"], "Stripe Payments")

    def test_11_get_adapter_by_name(self):
        adapter = self.engine.get_adapter("RevenueCat")
        self.assertEqual(adapter["app_id"], "app_022")

    def test_12_get_adapter_not_found(self):
        adapter = self.engine.get_adapter("app_non_existent")
        self.assertIn("error", adapter)

    def test_13_register_custom_adapter(self):
        res = self.engine.register_adapter("app_custom_999", "Custom AI Engine", "Analytics & AI")
        self.assertEqual(res["app_id"], "app_custom_999")
        self.assertEqual(len(self.engine.adapters_registry), 201)

    def test_14_execute_single_adapter_query(self):
        res = self.engine.execute_adapter_query("app_001", "FETCH_ENTITIES", {"limit": 10})
        self.assertEqual(res["status"], "QUERY_EXECUTED_SUCCESSFULLY")
        self.assertEqual(res["records_count"], 10)

    def test_15_execute_1000_queries_default(self):
        report = self.engine.execute_1000_queries(queries=1000, batch_size=100)
        self.assertEqual(report["total_queries_executed"], 1000)
        self.assertEqual(report["successful_queries"], 1000)
        self.assertIn("cryptographic_audit_hash", report)

    def test_16_execute_1000_queries_custom_batch_size(self):
        report = self.engine.execute_1000_queries(queries=200, batch_size=50)
        self.assertEqual(report["total_queries_executed"], 200)

    def test_17_execute_1000_queries_with_query_list(self):
        custom_queries = [{"app_id": "app_001", "query_type": "SYNC"} for _ in range(50)]
        report = self.engine.execute_1000_queries(queries=custom_queries)
        self.assertEqual(report["total_queries_executed"], 50)

    def test_18_execute_1000_queries_metrics(self):
        report = self.engine.execute_1000_queries(queries=100)
        self.assertGreater(report["throughput_qps"], 0.0)
        self.assertGreater(report["average_latency_ms"], 0.0)

    def test_19_run_adapters_audit(self):
        audit = self.engine.run_adapters_audit()
        self.assertEqual(audit["total_registered_adapters"], 200)
        self.assertEqual(audit["overall_status"], "MCP_200_ADAPTERS_FULLY_OPERATIONAL")

    def test_20_adapter_endpoints_supported(self):
        adapter = self.engine.get_adapter("app_001")
        self.assertGreaterEqual(len(adapter["endpoints_supported"]), 2)


# =============================================================================
# 2. VIRTUAL COMPUTER CLOUD ENGINE TESTS (20 Tests)
# =============================================================================
class TestVirtualComputerCloudEngine(unittest.TestCase):

    def setUp(self):
        self.vm_engine = VirtualComputerCloudEngine()

    def test_21_provision_default_instance(self):
        vm = self.vm_engine.provision_instance("vc_test_01")
        self.assertEqual(vm["status"], "RUNNING")
        self.assertEqual(vm["cpu_cores"], 4)
        self.assertEqual(vm["ram_gb"], 16)

    def test_22_provision_instance_types(self):
        vm_nano = self.vm_engine.provision_instance("vm_nano", instance_type="vc.nano")
        vm_ultra = self.vm_engine.provision_instance("vm_ultra", instance_type="vc.ultra")
        self.assertEqual(vm_nano["cpu_cores"], 1)
        self.assertEqual(vm_ultra["ram_gb"], 128)

    def test_23_provision_custom_specs(self):
        vm = self.vm_engine.provision_instance("vm_custom", cpu_cores=8, ram_gb=32, storage_gb=500)
        self.assertEqual(vm["cpu_cores"], 8)
        self.assertEqual(vm["ram_gb"], 32)
        self.assertEqual(vm["storage_gb"], 500)

    def test_24_supported_os_images(self):
        vm_ubuntu = self.vm_engine.provision_instance("vm_ubuntu", os_image="Ubuntu-24.04-LTS")
        self.assertEqual(vm_ubuntu["os_image"], "Ubuntu-24.04-LTS")

    def test_25_unsupported_os_fallback(self):
        vm = self.vm_engine.provision_instance("vm_invalid", os_image="Windows-95")
        self.assertEqual(vm["os_image"], "Sovereign-Linux-2026")

    def test_26_get_instance_status(self):
        vm = self.vm_engine.provision_instance("vm_status_check")
        status = self.vm_engine.get_instance_status(vm["instance_id"])
        self.assertEqual(status["status"], "RUNNING")
        self.assertEqual(status["telemetry"]["health"], "HEALTHY")

    def test_27_get_instance_status_not_found(self):
        status = self.vm_engine.get_instance_status("vci_invalid")
        self.assertEqual(status["status"], "NOT_FOUND")

    def test_28_list_instances_no_filters(self):
        self.vm_engine.provision_instance("vm_1")
        self.vm_engine.provision_instance("vm_2")
        instances = self.vm_engine.list_instances()
        self.assertEqual(len(instances), 2)

    def test_29_list_instances_tenant_filter(self):
        self.vm_engine.provision_instance("vm_tenant_a", tenant_id="tenant_A")
        self.vm_engine.provision_instance("vm_tenant_b", tenant_id="tenant_B")
        instances = self.vm_engine.list_instances(tenant_id="tenant_A")
        self.assertEqual(len(instances), 1)

    def test_30_list_instances_status_filter(self):
        vm = self.vm_engine.provision_instance("vm_run")
        self.vm_engine.stop_instance(vm["instance_id"])
        stopped = self.vm_engine.list_instances(status="STOPPED")
        self.assertEqual(len(stopped), 1)

    def test_31_execute_command_success(self):
        vm = self.vm_engine.provision_instance("vm_cmd")
        res = self.vm_engine.execute_command(vm["instance_id"], "uname -a")
        self.assertEqual(res["exit_code"], 0)
        self.assertIn("Linux", res["stdout"])

    def test_32_execute_command_docker(self):
        vm = self.vm_engine.provision_instance("vm_docker")
        res = self.vm_engine.execute_command(vm["instance_id"], "docker ps")
        self.assertEqual(res["exit_code"], 0)

    def test_33_execute_command_failure_simulation(self):
        vm = self.vm_engine.provision_instance("vm_fail")
        res = self.vm_engine.execute_command(vm["instance_id"], "make fail")
        self.assertEqual(res["exit_code"], 1)

    def test_34_execute_command_stopped_vm_fails(self):
        vm = self.vm_engine.provision_instance("vm_stopped_cmd")
        self.vm_engine.stop_instance(vm["instance_id"])
        res = self.vm_engine.execute_command(vm["instance_id"], "ls -la")
        self.assertEqual(res["status"], "EXECUTION_FAILED")

    def test_35_stop_instance(self):
        vm = self.vm_engine.provision_instance("vm_stop")
        res = self.vm_engine.stop_instance(vm["instance_id"])
        self.assertEqual(res["status"], "STOPPED")

    def test_36_start_instance(self):
        vm = self.vm_engine.provision_instance("vm_start")
        self.vm_engine.stop_instance(vm["instance_id"])
        res = self.vm_engine.start_instance(vm["instance_id"])
        self.assertEqual(res["status"], "RUNNING")

    def test_37_pause_instance(self):
        vm = self.vm_engine.provision_instance("vm_pause")
        res = self.vm_engine.pause_instance(vm["instance_id"])
        self.assertEqual(res["status"], "PAUSED")

    def test_38_scale_instance_resources(self):
        vm = self.vm_engine.provision_instance("vm_scale")
        scaled = self.vm_engine.scale_instance_resources(vm["instance_id"], cpu_cores=16, ram_gb=64)
        self.assertEqual(scaled["cpu_cores"], 16)
        self.assertEqual(scaled["ram_gb"], 64)

    def test_39_terminate_instance(self):
        vm = self.vm_engine.provision_instance("vm_term")
        res = self.vm_engine.terminate_instance(vm["instance_id"])
        self.assertEqual(res["status"], "TERMINATED")

    def test_40_run_vm_audit(self):
        audit = self.vm_engine.run_vm_audit()
        self.assertEqual(audit["overall_status"], "VM_CLOUD_ENGINE_OPERATIONAL")


# =============================================================================
# 3. SOVEREIGN MCP SERVER INTEGRATION TESTS (12 Tests)
# =============================================================================
class TestSovereignMCPServerIntegration(unittest.TestCase):

    def setUp(self):
        self.mcp = SovereignMCPServer()

    def test_41_server_has_adapters_engine(self):
        self.assertTrue(hasattr(self.mcp, "adapters_engine"))
        self.assertEqual(len(self.mcp.adapters_engine.adapters_registry), 200)

    def test_42_server_has_vm_engine(self):
        self.assertTrue(hasattr(self.mcp, "vm_engine"))

    def test_43_mcp_tool_200apps_adapters_list(self):
        res = self.mcp.handle_mcp_tool_call("mcp_200apps_adapters", {"action": "list"})
        self.assertIn("adapters", res)
        self.assertEqual(len(res["adapters"]), 200)

    def test_44_mcp_tool_200apps_adapters_get(self):
        res = self.mcp.handle_mcp_tool_call("mcp_200apps_adapters", {"action": "get", "app_id": "app_001"})
        self.assertEqual(res["name"], "QuickBooks Online")

    def test_45_mcp_tool_200apps_adapters_register(self):
        res = self.mcp.handle_mcp_tool_call("mcp_200apps_adapters", {
            "action": "register", "app_id": "app_mcp_custom", "name": "MCP Custom App"
        })
        self.assertEqual(res["app_id"], "app_mcp_custom")

    def test_46_mcp_tool_200apps_execute_1000(self):
        res = self.mcp.handle_mcp_tool_call("mcp_200apps_execute_1000", {"queries": 100})
        self.assertEqual(res["total_queries_executed"], 100)

    def test_47_mcp_tool_vm_instances_provision(self):
        res = self.mcp.handle_mcp_tool_call("mcp_vm_instances", {"action": "provision", "instance_name": "mcp_vm_01"})
        self.assertEqual(res["status"], "RUNNING")

    def test_48_mcp_tool_vm_instances_status(self):
        vm = self.mcp.vm_engine.provision_instance("mcp_vm_stat")
        res = self.mcp.handle_mcp_tool_call("mcp_vm_instances", {"action": "status", "instance_id": vm["instance_id"]})
        self.assertEqual(res["status"], "RUNNING")

    def test_49_mcp_tool_vm_instances_list(self):
        self.mcp.vm_engine.provision_instance("vm_list_mcp")
        res = self.mcp.handle_mcp_tool_call("mcp_vm_instances", {"action": "list"})
        self.assertIn("instances", res)

    def test_50_mcp_tool_vm_execute_command(self):
        vm = self.mcp.vm_engine.provision_instance("vm_exec_mcp")
        res = self.mcp.handle_mcp_tool_call("mcp_vm_execute_command", {"instance_id": vm["instance_id"], "command": "uname -a"})
        self.assertEqual(res["exit_code"], 0)

    def test_51_run_self_diagnostics_includes_new_audits(self):
        diag = self.mcp.run_self_diagnostics()
        self.assertIn("mcp_200_app_adapters_audit", diag)
        self.assertIn("virtual_computer_cloud_audit", diag)

    def test_52_json_rpc_tool_call_200apps(self):
        rpc_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "mcp_200apps_adapters", "arguments": {"action": "list"}}
        }
        res = self.mcp.handle_rpc_request(rpc_req)
        self.assertEqual(res["id"], 1)
        self.assertIn("content", res["result"])


# =============================================================================
# 4. DASHBOARD SERVER REST ENDPOINTS TESTS (12+ Tests)
# =============================================================================
class TestSovereignDashboardServerRESTEndpoints(unittest.TestCase):

    def test_53_rest_get_200apps_adapters_all(self):
        handler = MockHTTPRequestHandler(method="GET", path="/api/v1/mcp/200apps/adapters")
        handler.do_GET()
        self.assertEqual(handler.response_status, 200)
        self.assertEqual(handler.response_body["total"], 200)

    def test_54_rest_get_200apps_adapters_category_filter(self):
        handler = MockHTTPRequestHandler(method="GET", path="/api/v1/mcp/200apps/adapters?category=HR%20%26%20Payroll")
        handler.do_GET()
        self.assertEqual(handler.response_status, 200)
        self.assertEqual(len(handler.response_body["adapters"]), 20)

    def test_55_rest_get_200apps_adapters_by_app_id(self):
        handler = MockHTTPRequestHandler(method="GET", path="/api/v1/mcp/200apps/adapters?app_id=app_001")
        handler.do_GET()
        self.assertEqual(handler.response_status, 200)
        self.assertEqual(handler.response_body["name"], "QuickBooks Online")

    def test_56_rest_get_200apps_execute_1000(self):
        handler = MockHTTPRequestHandler(method="GET", path="/api/v1/mcp/200apps/execute_1000?queries=50")
        handler.do_GET()
        self.assertEqual(handler.response_status, 200)
        self.assertEqual(handler.response_body["total_queries_executed"], 50)

    def test_57_rest_get_vm_instances(self):
        handler = MockHTTPRequestHandler(method="GET", path="/api/v1/vm/instances")
        handler.do_GET()
        self.assertEqual(handler.response_status, 200)
        self.assertIn("instances", handler.response_body)

    def test_58_rest_get_vm_execute_command(self):
        handler = MockHTTPRequestHandler(method="GET", path="/api/v1/vm/execute_command?command=uname%20-a")
        handler.do_GET()
        self.assertEqual(handler.response_status, 200)
        self.assertEqual(handler.response_body["exit_code"], 0)

    def test_59_rest_post_200apps_adapters_list(self):
        handler = MockHTTPRequestHandler(method="POST", path="/api/v1/mcp/200apps/adapters", body={"action": "list"})
        handler.do_POST()
        self.assertEqual(handler.response_status, 200)
        self.assertEqual(handler.response_body["total"], 200)

    def test_60_rest_post_200apps_adapters_register(self):
        handler = MockHTTPRequestHandler(method="POST", path="/api/v1/mcp/200apps/adapters", body={
            "action": "register", "app_id": "app_rest_01", "name": "REST App", "category": "Analytics & AI"
        })
        handler.do_POST()
        self.assertEqual(handler.response_status, 200)
        self.assertEqual(handler.response_body["app_id"], "app_rest_01")

    def test_61_rest_post_200apps_execute_1000(self):
        handler = MockHTTPRequestHandler(method="POST", path="/api/v1/mcp/200apps/execute_1000", body={"queries": 100})
        handler.do_POST()
        self.assertEqual(handler.response_status, 200)
        self.assertEqual(handler.response_body["total_queries_executed"], 100)

    def test_62_rest_post_vm_instances_provision(self):
        handler = MockHTTPRequestHandler(method="POST", path="/api/v1/vm/instances", body={
            "action": "provision", "instance_name": "rest_vm_01", "instance_type": "vc.standard"
        })
        handler.do_POST()
        self.assertEqual(handler.response_status, 200)
        self.assertEqual(handler.response_body["status"], "RUNNING")

    def test_63_rest_post_vm_instances_lifecycle(self):
        # Provision
        h_prov = MockHTTPRequestHandler(method="POST", path="/api/v1/vm/instances", body={"action": "provision", "instance_name": "lifec_vm"})
        h_prov.do_POST()
        inst_id = h_prov.response_body["instance_id"]

        # Stop
        h_stop = MockHTTPRequestHandler(method="POST", path="/api/v1/vm/instances", body={"action": "stop", "instance_id": inst_id})
        h_stop.do_POST()
        self.assertEqual(h_stop.response_body["status"], "STOPPED")

        # Start
        h_start = MockHTTPRequestHandler(method="POST", path="/api/v1/vm/instances", body={"action": "start", "instance_id": inst_id})
        h_start.do_POST()
        self.assertEqual(h_start.response_body["status"], "RUNNING")

        # Terminate
        h_term = MockHTTPRequestHandler(method="POST", path="/api/v1/vm/instances", body={"action": "terminate", "instance_id": inst_id})
        h_term.do_POST()
        self.assertEqual(h_term.response_body["status"], "TERMINATED")

    def test_64_rest_post_vm_execute_command(self):
        h_prov = MockHTTPRequestHandler(method="POST", path="/api/v1/vm/instances", body={"action": "provision", "instance_name": "cmd_vm"})
        h_prov.do_POST()
        inst_id = h_prov.response_body["instance_id"]

        h_cmd = MockHTTPRequestHandler(method="POST", path="/api/v1/vm/execute_command", body={"instance_id": inst_id, "command": "uname -a"})
        h_cmd.do_POST()
        self.assertEqual(h_cmd.response_status, 200)
        self.assertEqual(h_cmd.response_body["exit_code"], 0)


if __name__ == "__main__":
    unittest.main()
