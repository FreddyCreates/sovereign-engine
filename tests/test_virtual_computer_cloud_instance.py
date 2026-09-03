"""
Exhaustive Automated Test Suite for Virtual Computer Cloud Instance Engine.
5 Core Test Scenarios:
1. Agent VM Provisioning & Lifecycle Management
2. Virtual Terminal & Shell Command Execution Engine
3. Virtual Block Storage Filesystem, Quota Enforcement & Snapshot System
4. Telemetry Engine, Mathematical Load Average & Thermal Modeling
5. Cloud Instance Orchestrator, Multi-VM Pool & RevenueCat Quota Enforcement
"""

import unittest
import time
import pytest
from sovereign_infrastructure.nextgen_systems.virtual_computer_cloud_instance import (
    VirtualComputerCloudInstance,
    AgentVMInstance,
    VirtualTerminal,
    VirtualDisk,
    TelemetryEngine,
    StorageQuotaExceededError,
    VMStateError
)


class TestVirtualComputerCloudInstance(unittest.TestCase):

    def setUp(self):
        self.cloud = VirtualComputerCloudInstance()

    def test_01_vm_provisioning_and_lifecycle(self):
        """Test 1: Verifies VM creation and lifecycle status transitions."""
        vm = self.cloud.provision_vm(
            agent_id="agent_alpha",
            vcpus=4,
            ram_mb=8192.0,
            storage_gb=50.0,
            tenant_id="tenant_fintech",
            entitlement_tier="enterprise"
        )
        self.assertIsNotNone(vm.vm_id)
        self.assertEqual(vm.status, "RUNNING")
        self.assertEqual(vm.agent_id, "agent_alpha")
        self.assertEqual(vm.vcpus, 4)

        # Lifecycle Transitions
        vm.suspend()
        self.assertEqual(vm.status, "SUSPENDED")

        vm.resume()
        self.assertEqual(vm.status, "RUNNING")

        # Invalid transition test
        with self.assertRaises(VMStateError):
            vm.resume()  # Cannot resume an already RUNNING VM

        vm.stop()
        self.assertEqual(vm.status, "STOPPED")

        vm.terminate()
        self.assertEqual(vm.status, "TERMINATED")

    def test_02_virtual_terminal_and_command_execution(self):
        """Test 2: Verifies terminal command execution, filesystem commands, env vars, and exit codes."""
        vm = self.cloud.provision_vm(
            agent_id="agent_dev",
            vcpus=2,
            ram_mb=4096.0,
            tenant_id="tenant_dev",
            entitlement_tier="pro"
        )

        # 1. pwd
        res_pwd = vm.execute_terminal_command("pwd")
        self.assertEqual(res_pwd["exit_code"], 0)
        self.assertEqual(res_pwd["stdout"], "/home/agent")

        # 2. mkdir & cd
        vm.execute_terminal_command("mkdir workspace")
        res_cd = vm.execute_terminal_command("cd workspace")
        self.assertEqual(res_cd["exit_code"], 0)
        res_pwd2 = vm.execute_terminal_command("pwd")
        self.assertEqual(res_pwd2["stdout"], "/home/agent/workspace")

        # 3. echo to file & cat
        vm.execute_terminal_command('echo "SOVEREIGN_OS_CORE_ONLINE" > status.txt')
        res_cat = vm.execute_terminal_command("cat status.txt")
        self.assertEqual(res_cat["exit_code"], 0)
        self.assertIn("SOVEREIGN_OS_CORE_ONLINE", res_cat["stdout"])

        # 4. export & env
        vm.execute_terminal_command("export ENGINE_MODE=QUANTUM")
        res_env = vm.execute_terminal_command("env")
        self.assertIn("ENGINE_MODE=QUANTUM", res_env["stdout"])

        # 5. Invalid command error handling
        res_err = vm.execute_terminal_command("non_existent_binary_xyz")
        self.assertIn(res_err["exit_code"], [1, 127])

    def test_03_virtual_disk_storage_and_snapshots(self):
        """Test 3: Verifies disk storage writes, quota overflow, snapshot creation and restoration."""
        import tempfile
        test_dir = tempfile.mkdtemp(prefix="test_disk_")
        disk = VirtualDisk(disk_id="test_disk", capacity_gb=0.001, root_dir=test_dir)  # ~1MB capacity

        # Write valid file
        meta = disk.write_file("/home/agent/config.json", '{"theme": "dark", "version": "2.5"}')
        self.assertGreater(meta["size"], 0)
        self.assertEqual(disk.read_file("/home/agent/config.json"), '{"theme": "dark", "version": "2.5"}')

        # Quota Exceeded Test
        large_content = "X" * (2 * 1024 * 1024)  # 2MB exceeds 1MB quota
        with self.assertRaises(StorageQuotaExceededError):
            disk.write_file("/home/agent/overflow.dat", large_content)

        # Snapshot & Restore Test
        disk.create_snapshot("initial_state")
        disk.write_file("/home/agent/config.json", '{"theme": "light", "version": "3.0"}')
        self.assertEqual(disk.read_file("/home/agent/config.json"), '{"theme": "light", "version": "3.0"}')

        disk.restore_snapshot("initial_state")
        self.assertEqual(disk.read_file("/home/agent/config.json"), '{"theme": "dark", "version": "2.5"}')

    def test_04_telemetry_engine_and_mathematical_load(self):
        """Test 4: Verifies CPU/RAM calculations, decay modeling, and thermal monitoring."""
        telemetry = TelemetryEngine(vcpus=8, total_ram_mb=16384.0)
        
        # Initial Telemetry Check
        metrics1 = telemetry.update_telemetry(active_processes=4, iops=150.0)
        self.assertEqual(metrics1["vcpus"], 8)
        self.assertGreater(metrics1["cpu_utilization_pct"], 0.0)
        self.assertGreater(metrics1["load_average"]["1min"], 0.0)
        self.assertFalse(metrics1["thermal_throttled"])

        # RAM Allocation & Release
        telemetry.allocate_ram(4096.0)
        self.assertEqual(telemetry.used_ram_mb, 4608.0)
        metrics2 = telemetry.update_telemetry(active_processes=6, iops=500.0)
        self.assertGreater(metrics2["ram_utilization_pct"], 25.0)

        telemetry.release_ram(4096.0)
        self.assertEqual(telemetry.used_ram_mb, 512.0)

    def test_05_cloud_orchestrator_multi_vm_pool_and_revenuecat_quotas(self):
        """Test 5: Verifies cloud orchestrator VM pool, RevenueCat tier quotas, and aggregate telemetry."""
        # 1. Provision VMs under Free Tier (Limit = 2 VMs)
        vm1 = self.cloud.provision_vm(agent_id="agent_1", tenant_id="free_tenant", entitlement_tier="free")
        vm2 = self.cloud.provision_vm(agent_id="agent_2", tenant_id="free_tenant", entitlement_tier="free")
        self.assertIsNotNone(vm1)
        self.assertIsNotNone(vm2)

        # 3rd VM under Free Tier should fail quota check
        with self.assertRaises(PermissionError):
            self.cloud.provision_vm(agent_id="agent_3", tenant_id="free_tenant", entitlement_tier="free")

        # 2. Provision VM under Enterprise Tier
        vm_ent = self.cloud.provision_vm(agent_id="agent_ent", tenant_id="enterprise_tenant", entitlement_tier="enterprise")
        self.assertIsNotNone(vm_ent)

        # 3. Aggregate Telemetry Summary Check
        summary = self.cloud.get_cloud_telemetry_summary()
        self.assertEqual(summary["total_vms_provisioned"], 3)
        self.assertEqual(summary["active_vms_running"], 3)
        self.assertGreater(summary["aggregate_vcpus_allocated"], 0)
        self.assertEqual(summary["health_status"], "HEALTHY")


if __name__ == "__main__":
    unittest.main()
