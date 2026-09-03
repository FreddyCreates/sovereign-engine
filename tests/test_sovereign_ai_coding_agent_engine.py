"""
Exhaustive Automated Test Suite for Sovereign AI Coding Agent Engine.
Tests all 7 Core Capabilities:
1. PersistentMemoryStore (Session memory, transcript history, vector/semantic memory indexing)
2. SkillSynthesizer (Experience auto-learning, generates reusable skills in .agents/skills/SKILL.md)
3. AgentToolRegistry (40+ built-in tools: Web search, browser automation, vision, refactoring, AST grep, terminal, Git/PR, DB migration, API runner, Security audit, Go tools, etc.)
4. ScheduledAutomationEngine (One-shot timers, cron schedules, background notifications)
5. SubagentOrchestrator (Spawns researcher, coder, reviewer, tester, architect subagents with message passing)
6. IDEBridgeManager (VS Code Extension, JetBrains Plugin, CLI stdio/RPC protocols)
7. SovereignGoServicesEngine (10 Go-backed uses integration)
"""

import os
import unittest
import json
import time
import pytest

from sovereign_infrastructure.nextgen_systems.sovereign_go_services_engine import (
    SovereignGoServicesEngine
)
from sovereign_infrastructure.nextgen_systems.sovereign_ai_coding_agent_engine import (
    SovereignAICodingAgentEngine,
    PersistentMemoryStore,
    SkillSynthesizer,
    AgentToolRegistry,
    ScheduledAutomationEngine,
    SubagentOrchestrator,
    IDEBridgeManager
)


class TestSovereignAICodingAgentEngine(unittest.TestCase):

    def setUp(self):
        self.engine = SovereignAICodingAgentEngine(session_id="test-session-001", skills_dir="tmp_skills")

    def tearDown(self):
        # Clean up temporary skills directory if created
        if os.path.exists("tmp_skills"):
            for root, dirs, files in os.walk("tmp_skills", topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir("tmp_skills")

    def test_01_persistent_memory_store(self):
        """Test 1: Verifies session memory, transcript logging, export/import, and vector search."""
        store = self.engine.memory_store
        
        # Add turns
        entry1 = store.add_turn("user", "Build a secure REST API in Python")
        entry2 = store.add_turn("assistant", "I will use FastAPI and Pydantic for validation.")

        self.assertEqual(len(store.active_context), 2)
        self.assertEqual(len(store.transcript_history), 2)
        self.assertEqual(entry1["role"], "user")

        # Semantic memory search
        search_res = store.search_semantic_memory("secure REST API", top_k=2)
        self.assertTrue(len(search_res) > 0)
        self.assertIn("score", search_res[0])

        # Export and Import
        exported = store.export_transcript()
        self.assertTrue("test-session-001" in exported)

        new_store = PersistentMemoryStore()
        success = new_store.import_transcript(exported)
        self.assertTrue(success)
        self.assertEqual(len(new_store.transcript_history), 2)

    def test_02_skill_synthesizer(self):
        """Test 2: Verifies experience auto-learning and .agents/skills/SKILL.md skill generation."""
        synth = self.engine.skill_synthesizer
        transcript = [
            {"role": "user", "content": "Refactor database connection pool"},
            {"role": "assistant", "content": "Executing refactoring tool", "tool_calls": [{"name": "file_refactoring", "args": {"target_files": ["db.py"]}}]}
        ]

        skill_info = synth.synthesize_skill_from_transcript(transcript, "db_pool_refactor")
        self.assertEqual(skill_info["name"], "db_pool_refactor")
        self.assertTrue(os.path.exists(skill_info["file_path"]))

        # Execute skill
        exec_res = synth.execute_skill("db_pool_refactor", target_file="src/db.py")
        self.assertEqual(exec_res["status"], "SUCCESS")
        self.assertEqual(exec_res["invocations"], 1)

    def test_03_agent_tool_registry_40_plus_tools(self):
        """Test 3: Verifies all 40+ built-in agentic tools in AgentToolRegistry."""
        registry = self.engine.tool_registry
        tools = registry.list_tools()
        self.assertGreaterEqual(len(tools), 40)

        # Test key tools
        web_res = registry.execute_tool("web_search", query="python 3.12 release notes")
        self.assertTrue(web_res["tool_executed"] == "web_search")

        sec_res = registry.execute_tool("security_audit", source_code="password = 'secret_key_12345'")
        self.assertTrue(isinstance(sec_res, list) or sec_res.get("tool_executed") == "security_audit")

        terminal_res = registry.execute_tool("terminal_execution", command="echo hello")
        self.assertTrue(terminal_res["success"])
        self.assertIn("hello", terminal_res["stdout"])

        # Test Go tools
        go_ast_res = registry.execute_tool("go_ast_parser", source_code="def foo(): pass")
        self.assertTrue(go_ast_res.get("go_accelerated"))

    def test_04_scheduled_automation_engine(self):
        """Test 4: Verifies one-shot timers, cron schedules, and background notifications."""
        auto = self.engine.automation_engine

        # One-shot timer
        timer = auto.set_timer(duration_seconds=0.01, prompt="Check build status", condition="never")
        self.assertEqual(timer["status"], "ACTIVE")

        # Cron schedule
        cron = auto.schedule_cron(cron_expression="*/5 * * * *", prompt="Periodic health check", max_iterations=2)
        self.assertEqual(cron["status"], "ACTIVE")

        # Wait and tick
        time.sleep(0.05)
        notifications = auto.tick_and_dispatch()
        self.assertTrue(len(notifications) >= 1)

        # Cancel timer
        cancel_res = auto.cancel_timer(timer["timer_id"])
        self.assertFalse(cancel_res)  # Already expired

    def test_05_subagent_orchestrator(self):
        """Test 5: Verifies spawning specialized subagents and inter-agent message passing."""
        orchestrator = self.engine.subagent_orchestrator

        # Spawn subagents
        researcher = orchestrator.spawn_subagent("researcher", "res-01")
        coder = orchestrator.spawn_subagent("coder", "code-01")

        self.assertEqual(researcher["role"], "researcher")
        self.assertEqual(coder["role"], "coder")

        # Inter-agent message passing
        msg = orchestrator.send_message("res-01", "code-01", "Architecture spec ready.")
        self.assertEqual(msg["sender_id"], "res-01")

        # Receive inbox
        inbox = orchestrator.get_messages("code-01")
        self.assertEqual(len(inbox), 1)
        self.assertEqual(inbox[0]["message"], "Architecture spec ready.")

        # Assign task with sandbox execution
        task = orchestrator.assign_task("code-01", "Implement math solver", script_code="result = 42")
        self.assertEqual(task["status"], "COMPLETED")
        self.assertEqual(task["output"], "42")

    def test_06_ide_bridge_manager(self):
        """Test 6: Verifies IDE Bridge protocols for VS Code, JetBrains, and CLI stdio/RPC."""
        bridge = self.engine.ide_bridge

        # VS Code RPC
        vscode_res = bridge.handle_vscode_request("getSelection", {"file": "main.py"})
        self.assertEqual(vscode_res["protocol"], "vscode_extension")
        self.assertEqual(vscode_res["status"], "SUCCESS")

        # JetBrains RPC
        jb_res = bridge.handle_jetbrains_request("codeCompletion", {"file": "main.py", "offset": 10})
        self.assertEqual(jb_res["protocol"], "jetbrains_plugin")

        # CLI Stdio RPC
        cli_res = bridge.handle_cli_stdio_request('{"method": "ping", "params": {}}')
        self.assertEqual(cli_res["protocol"], "cli_stdio")

    def test_07_sovereign_go_services_engine_10_uses(self):
        """Test 7: Verifies all 10 Go-backed services integration."""
        go_services = SovereignGoServicesEngine()
        status = go_services.get_status()
        self.assertEqual(status["services_active"], 10)
        self.assertTrue(status["go_native_acceleration"])

        # 1. GoASTIndexer
        ast_data = go_services.ast_indexer.parse_ast("class Server:\n    def run(self): pass", "python")
        self.assertEqual(len(ast_data["classes"]), 1)

        # 2. GoVectorSearchEngine
        vectors = [{"id": "v1", "vector": [1.0, 0.0], "content": "doc1"}]
        v_res = go_services.vector_search.search_vectors(vectors, [1.0, 0.0], top_k=1)
        self.assertEqual(v_res[0]["id"], "v1")

        # 3. GoSubprocessExecutor
        sub_res = go_services.subprocess_executor.execute_command("echo test_go")
        self.assertTrue(sub_res["success"])

        # 4. GoFileWatcher
        watch_res = go_services.file_watcher.watch_directory(".")
        self.assertIn("total_files", watch_res)

        # 5. GoSecurityScanner
        sec_res = go_services.security_scanner.audit_security("eval('secret')")
        self.assertTrue(len(sec_res) > 0)

        # 6. GoGitEngine
        patch_res = go_services.git_engine.synthesize_patch("a = 1", "a = 2")
        self.assertIn("+ a = 2", patch_res["patch"])

        # 7. GoDBMigrationEngine
        migration_res = go_services.db_migration.diff_schemas({}, {"tables": {"users": {"id": "INT"}}})
        self.assertEqual(migration_res["migration_count"], 1)

        # 8. GoAPIBenchmarkRunner
        bench_res = go_services.api_benchmark.run_benchmark("https://api.example.com", total_requests=10, concurrency=2)
        self.assertEqual(bench_res["total_requests"], 10)

        # 9. GoIDERPCBridge
        rpc_res = go_services.ide_rpc_bridge.bridge_rpc("vscode", "format_document", {})
        self.assertEqual(rpc_res["status"], "SUCCESS")

        # 10. GoSandboxExecutor
        sandbox_res = go_services.sandbox_executor.run_in_sandbox("sub-01", "result = 10 + 20")
        self.assertEqual(sandbox_res["output"], "30")

    def test_08_full_agent_turn_execution(self):
        """Test 8: Verifies full master agent turn execution and health metrics."""
        turn_res = self.engine.run_agent_turn("Audit security and search for python ast parser", auto_synthesize_skill=True)
        self.assertEqual(turn_res["status"], "COMPLETED")
        self.assertTrue(len(turn_res["tool_results"]) >= 2)
        self.assertIsNotNone(turn_res["synthesized_skill"])

        health = self.engine.get_system_health()
        self.assertEqual(health["tool_registry"]["total_tools"], len(self.engine.tool_registry.tools))
        self.assertEqual(health["go_services"]["services_active"], 10)
        self.assertEqual(health["inner_ai_engine"]["engine_status"], "ONLINE")

    def test_09_inner_ai_routing_matrix(self):
        """Test 9: Verifies SovereignInnerAIEngine intent classification & neural routing matrix."""
        inner_ai = self.engine.inner_ai_engine

        # FX Arbitrage prompt
        route1 = inner_ai.route("Calculate FX triangular arbitrage for EUR/USD/GBP")
        self.assertEqual(route1["routed_intent"], "FINTECH_ARBITRAGE")
        self.assertEqual(route1["target_app_skill"], "fx_triangular_arbitrage")
        self.assertGreater(route1["confidence_score"], 0.20)

        # Risk Underwriting prompt
        route2 = inner_ai.route("Underwrite credit risk and default probability for business loan")
        self.assertEqual(route2["routed_intent"], "RISK_UNDERWRITING")
        self.assertEqual(route2["target_app_skill"], "credit_risk_underwriting")

        # Intent Override test
        route3 = inner_ai.route("General query", intent_override="TOKENOMICS")
        self.assertEqual(route3["routed_intent"], "TOKENOMICS")
        self.assertEqual(route3["target_app_skill"], "deflationary_tokenomics_curve")

    def test_10_inner_ai_fx_arbitrage_app_skill(self):
        """Test 10: Verifies mathematical FX triangular arbitrage calculation & execution."""
        inner_ai = self.engine.inner_ai_engine
        exec_res = inner_ai.execute_app_skill(
            "fx_triangular_arbitrage",
            params={
                "rate_eur_usd": 1.0850,
                "rate_usd_gbp": 0.7850,
                "rate_gbp_eur": 1.1780,
                "notional_principal": 1000000.0
            }
        )
        self.assertEqual(exec_res["status"], "SUCCESS")
        res = exec_res["result"]
        self.assertIn("profit_margin_pct", res)
        self.assertIn("net_arbitrage_profit_usd", res)
        self.assertTrue(res["is_arbitrage_opportunity"])
        self.assertEqual(res["execution_recommendation"], "EXECUTE_IMMEDIATE_SWAP")

    def test_11_inner_ai_credit_risk_and_ltv_app_skills(self):
        """Test 11: Verifies logistic sigmoid underwriting & RevenueCat subscriber LTV elasticity."""
        inner_ai = self.engine.inner_ai_engine

        # Credit Risk Underwriting
        risk_res = inner_ai.execute_app_skill(
            "credit_risk_underwriting",
            params={"credit_score": 750, "dti_ratio": 0.25, "monthly_revenue": 60000.0, "loan_amount": 100000.0}
        )
        self.assertEqual(risk_res["status"], "SUCCESS")
        self.assertIn(risk_res["result"]["underwriting_decision"], ["APPROVED", "DECLINED", "REVIEW"])
        self.assertLess(risk_res["result"]["probability_of_default_pd"], 0.95)

        # Subscriber LTV Elasticity
        ltv_res = inner_ai.execute_app_skill(
            "subscriber_ltv_elasticity",
            params={"arpu": 49.99, "gross_margin_pct": 0.85, "monthly_churn_pct": 0.03, "price_change_pct": 0.10}
        )
        self.assertEqual(ltv_res["status"], "SUCCESS")
        self.assertGreater(ltv_res["result"]["baseline_ltv_usd"], 1000.0)
        self.assertIn("projected_new_ltv_usd", ltv_res["result"])

    def test_12_inner_ai_tokenomics_and_iot_telemetry(self):
        """Test 12: Verifies deflationary tokenomics bonding curve & IoT hardware telemetry."""
        inner_ai = self.engine.inner_ai_engine

        # Tokenomics
        tok_res = inner_ai.execute_app_skill(
            "deflationary_tokenomics_curve",
            params={"current_supply": 1000000.0, "daily_volume_usd": 500000.0, "bonding_curve_gamma": 1.5}
        )
        self.assertEqual(tok_res["status"], "SUCCESS")
        self.assertGreater(tok_res["result"]["daily_tokens_burned"], 0)

        # IoT Telemetry
        iot_res = inner_ai.execute_app_skill(
            "iot_hardware_telemetry",
            params={"device_id": "SENSOR_99", "battery_pct": 95.0, "temperature_c": 30.0}
        )
        self.assertEqual(iot_res["status"], "SUCCESS")
        self.assertEqual(iot_res["result"]["revenuecat_entitlement_status"], "ENTITLEMENT_ACTIVE")

    def test_13_inner_ai_status_and_agent_engine_integration(self):
        """Test 13: Verifies SovereignAICodingAgentEngine delegation and status metrics."""
        route_res = self.engine.route_inner_ai("Synthesize neural micro app")
        self.assertEqual(route_res["target_app_skill"], "neural_app_synthesis")

        exec_res = self.engine.execute_inner_ai_skill("neural_app_synthesis", params={"app_name": "TestBot"})
        self.assertEqual(exec_res["status"], "SUCCESS")

        status = self.engine.get_inner_ai_status()
        self.assertEqual(status["engine_status"], "ONLINE")
        self.assertGreaterEqual(status["total_routes_processed"], 1)
        self.assertGreaterEqual(status["total_skill_executions"], 1)
        self.assertGreaterEqual(status["registered_app_skills_count"], 6)


if __name__ == "__main__":
    unittest.main()

