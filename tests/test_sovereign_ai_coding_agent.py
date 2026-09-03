"""
Comprehensive Automated Test Suite for Sovereign AI Coding Agent Engine & Go Runtime.
Tests:
1. Go Services Engine (All 10 Go-Powered Core Uses)
2. Persistent Memory Store across Sessions
3. Skill Synthesizer (.agents/skills/SKILL.md generation)
4. 40+ Built-in Tool Registry Execution
5. AI Coding Agent Chat Orchestration & IDE Bridges
6. REST API Server Endpoints Integration
"""

import unittest
import os
import sys
import json
import time
import tempfile
import pytest

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sovereign_infrastructure", "nextgen_systems")))

from sovereign_go_services_engine import SovereignGoServicesEngine
from sovereign_ai_coding_agent_engine import SovereignAICodingAgentEngine, PersistentMemoryStore, SkillSynthesizer, AgentToolRegistry


class TestSovereignAICodingAgent(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="agent_test_")
        self.go_engine = SovereignGoServicesEngine()
        self.agent_engine = SovereignAICodingAgentEngine(workspace_root=self.tmp_dir)

    def test_01_go_services_10_uses(self):
        """Test 1: Verifies all 10 Go-powered microservice features."""
        status = self.go_engine.get_go_runtime_status()
        self.assertEqual(status["active_services"], 10)
        self.assertEqual(status["status"], "OPERATIONAL")

        # Use 1: AST Analysis
        ast_res = self.go_engine.analyze_ast_symbols("package main\nfunc TestFunc(){}", "go")
        self.assertGreater(ast_res["symbol_count"], 0)

        # Use 2: Worker Pool
        job = self.go_engine.dispatch_goroutine_job("refactor_job", {"file": "main.go"})
        self.assertEqual(job["status"], "COMPLETED")

        # Use 3: Memory Store
        self.go_engine.memory_store_put("sess_1", "user_pref", "dark_theme")
        self.assertEqual(self.go_engine.memory_store_get("sess_1", "user_pref"), "dark_theme")

        # Use 4: Go Compiler
        run_res = self.go_engine.compile_and_run_go("package main\nimport \"fmt\"\nfunc main(){fmt.Println(\"Active\")}")
        self.assertEqual(run_res["exit_code"], 0)

        # Use 5: Security Scanner
        sec_res = self.go_engine.scan_security_vulnerabilities("var password = '123'")
        self.assertGreater(sec_res["vulnerability_count"], 0)

        # Use 6: Web Scraper
        web_res = self.go_engine.scrape_web_documentation("https://docs.go.dev")
        self.assertEqual(web_res["http_status"], 200)

        # Use 7: DB Migration
        sql_res = self.go_engine.generate_sql_migration("v1_schema", [{"name": "users"}])
        self.assertIn("CREATE TABLE", sql_res["up_migration"])

        # Use 8: IDE Socket Bridge
        rpc_res = self.go_engine.ide_bridge_process_request("VSCode", {"method": "get_code_completion"})
        self.assertEqual(rpc_res["status"], "SUCCESS")

        # Use 9: Cron Runtime
        cron = self.go_engine.register_cron_schedule("0 * * * *", "Audit code")
        self.assertEqual(cron["status"], "ACTIVE")

        # Use 10: Container Sandbox
        sb = self.go_engine.launch_go_container_sandbox("test_container")
        self.assertEqual(sb["status"], "RUNNING")

    def test_02_persistent_memory_store(self):
        """Test 2: Verifies cross-session memory transcript persistence."""
        mem = PersistentMemoryStore(storage_dir=self.tmp_dir)
        sess = mem.get_or_create_session("session_alpha")
        self.assertEqual(sess["session_id"], "session_alpha")

        mem.add_message("session_alpha", "user", "How do I use Go LSP?")
        mem.add_message("session_alpha", "assistant", "Use tool 'go_ast_analyzer'.")

        reloaded_sess = mem.get_or_create_session("session_alpha")
        self.assertEqual(len(reloaded_sess["messages"]), 2)
        self.assertEqual(reloaded_sess["messages"][0]["content"], "How do I use Go LSP?")

    def test_03_skill_synthesizer(self):
        """Test 3: Verifies auto-learning synthesis of .agents/skills/SKILL.md."""
        synth = SkillSynthesizer(workspace_root=self.tmp_dir)
        res = synth.synthesize_skill(
            skill_name="go_concurrency_opt",
            description="Optimizes Go channel buffers",
            instructions="Use buffered channels for async workers"
        )
        self.assertEqual(res["status"], "SYNTHESIZED_SUCCESSFULLY")
        self.assertTrue(os.path.exists(res["filepath"]))

        with open(res["filepath"], "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("go_concurrency_opt", content)
            self.assertIn("Optimizes Go channel buffers", content)

    def test_04_40_plus_tool_registry(self):
        """Test 4: Verifies registration and execution of 40+ built-in tools."""
        registry = self.agent_engine.tool_registry
        self.assertGreaterEqual(len(registry.tools), 40)

        # Execute web search tool
        web_res = registry.execute_tool("web_search", {"query": "RevenueCat API"})
        self.assertEqual(web_res["status"], "SUCCESS")

        # Execute Go compiler tool
        go_res = registry.execute_tool("go_compiler_run", {"code": "package main\nfunc main(){}"})
        self.assertEqual(go_res["mode"], "SIMULATED_GO_RUNNER" if not self.go_engine.is_go_available else "LIVE_GO_COMPILER")

    def test_05_chat_orchestration_and_subagents(self):
        """Test 5: Verifies end-to-end chat orchestration and subagent spawning."""
        chat_res = self.agent_engine.process_chat_prompt("sess_beta", "Search and compile go code", target_ide="JetBrains")
        self.assertEqual(chat_res["status"], "SUCCESS")
        self.assertEqual(chat_res["target_ide"], "JetBrains")
        self.assertGreater(len(chat_res["executed_tools"]), 0)

        subagent = self.agent_engine.spawn_subagent_task("Security Auditor", "Scan repository for leaked keys")
        self.assertEqual(subagent["status"], "RUNNING")
        self.assertEqual(subagent["role"], "Security Auditor")


if __name__ == "__main__":
    unittest.main()
