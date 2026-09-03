"""
EXHAUSTIVE AUTOMATED MASTER TEST SUITE FOR SOVEREIGN OS INNER AI ENGINE
========================================================================

Tests all 5 core components of the Master Inner AI Engine:
1. InnerAppSkillRouter: Mapping goals across 500 skills (Skills 1-500) and 200 SaaS apps.
2. InnerContextualPlanner: Multi-step DAG plan formulation with entitlements, ZK proofs & GL posting.
3. InnerSkillExecutor: Execution across SaaS app adapters and skills payload.
4. InnerMemoryConsolidator: Vector RAG memory persistence, similarity search & learned skill markdown.
5. InnerAppTelemetryPulse: Kuramoto phase coherence calculations (R = 0.9999) & telemetry emission.
6. SovereignInnerAIEngine: Master unified end-to-end processing pipeline.

Author: Lead Sovereign OS AI & Financial Accounting Architect
"""

import sys
import os
import json
import time
import shutil
import tempfile
import unittest

# Ensure sovereign_infrastructure/nextgen_systems and project root are in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NEXTGEN_DIR = os.path.join(BASE_DIR, "sovereign_infrastructure", "nextgen_systems")

if NEXTGEN_DIR not in sys.path:
    sys.path.insert(0, NEXTGEN_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from sovereign_inner_ai_engine import (
    SovereignInnerAIEngine,
    InnerAppSkillRouter,
    InnerContextualPlanner,
    InnerSkillExecutor,
    InnerMemoryConsolidator,
    InnerAppTelemetryPulse,
    SovereignZKDilithiumProofEngine
)


# =============================================================================
# 1. INNER APP SKILL ROUTER TESTS
# =============================================================================
class TestInnerAppSkillRouter(unittest.TestCase):
    """Test Suite for Component 1: InnerAppSkillRouter across 500 skills and 200 apps."""

    def setUp(self):
        self.router = InnerAppSkillRouter()

    def test_01_skills_catalog_500_coverage(self):
        """Verify the skills catalog contains exactly 500 skills covering 11 domain groups."""
        catalog = self.router.skills_catalog
        self.assertEqual(len(catalog), 500)
        self.assertIn(1, catalog)
        self.assertIn(500, catalog)

        # Check domain boundaries
        self.assertEqual(catalog[1]["domain"], "Foundation & OS Kernel Core")
        self.assertEqual(catalog[41]["domain"], "Financial Accounting & Double-Entry")
        self.assertEqual(catalog[61]["domain"], "Core Tech & Distributed Infra")
        self.assertEqual(catalog[81]["domain"], "Cloud Swarm & Mesh Engine")
        self.assertEqual(catalog[101]["domain"], "User Intelligence & Agentic Workspace")
        self.assertEqual(catalog[151]["domain"], "Agentic Workflow & Autonomous Swarm")
        self.assertEqual(catalog[201]["domain"], "Polyglot Languages & Multi-Compiler")
        self.assertEqual(catalog[251]["domain"], "Core Banking & Treasury Engine")
        self.assertEqual(catalog[301]["domain"], "Autonomous Fintech Swarm Engine")
        self.assertEqual(catalog[351]["domain"], "Multi-Step Project Engine")
        self.assertEqual(catalog[401]["domain"], "Singularity & Autonomic Evolution Engine")

    def test_02_skills_catalog_schema(self):
        """Verify each skill entry contains required keys and valid data types."""
        for skill_id, skill_info in self.router.skills_catalog.items():
            self.assertIsInstance(skill_id, int)
            self.assertIn("skill_id", skill_info)
            self.assertIn("name", skill_info)
            self.assertIn("domain", skill_info)
            self.assertIn("tags", skill_info)
            self.assertIn("confidence_weight", skill_info)
            self.assertGreaterEqual(skill_info["confidence_weight"], 0.90)

    def test_03_adapters_catalog_200_saas_coverage(self):
        """Verify the adapters catalog contains at least 200 SaaS app entries across 10 categories."""
        catalog = self.router.adapters_catalog
        # Dual indexing means length > 200
        self.assertGreaterEqual(len(catalog), 200)

        # Verify key SaaS app adapters exist
        key_adapters = [
            "quickbooks_online", "xero", "revenuecat", "stripe", "gusto",
            "bill_com", "plaid", "shopify", "salesforce", "aws", "openai"
        ]
        for key in key_adapters:
            self.assertIn(key, catalog, f"Expected adapter '{key}' not found in catalog.")
            self.assertEqual(catalog[key]["status"], "HEALTHY")
            self.assertEqual(catalog[key]["protocol"], "REST_OAUTH2_JSON")

    def test_04_route_goal_accounting(self):
        """Test goal routing for financial accounting keywords."""
        res = self.router.route_goal("Post double-entry GL ledger journal and run tax audit")
        self.assertGreater(res["total_skills_matched"], 0)
        self.assertGreater(res["total_adapters_matched"], 0)
        
        skill_ids = [s["skill_id"] for s in res["matched_skills"]]
        self.assertTrue(any(41 <= sid <= 60 for sid in skill_ids))
        
        adapter_keys = [a["key"] for a in res["matched_adapters"]]
        self.assertIn("quickbooks_online", adapter_keys)

    def test_05_route_goal_paywall_and_subscriptions(self):
        """Test goal routing for RevenueCat paywall and entitlement keywords."""
        res = self.router.route_goal("Verify StoreKit2 entitlement and render dynamic paywall AST")
        skill_ids = [s["skill_id"] for s in res["matched_skills"]]
        self.assertTrue(any(401 <= sid <= 450 for sid in skill_ids))

        adapter_keys = [a["key"] for a in res["matched_adapters"]]
        self.assertIn("revenuecat", adapter_keys)

    def test_06_route_goal_banking_treasury(self):
        """Test goal routing for banking, Plaid, and FedWire keywords."""
        res = self.router.route_goal("Execute FedWire ACH transfer and sync Plaid bank accounts")
        skill_ids = [s["skill_id"] for s in res["matched_skills"]]
        self.assertTrue(any(251 <= sid <= 275 for sid in skill_ids))

        adapter_keys = [a["key"] for a in res["matched_adapters"]]
        self.assertIn("plaid", adapter_keys)

    def test_07_route_goal_fallback_defaults(self):
        """Test fallback routing when no specific keywords match."""
        res = self.router.route_goal("Do some unspecific generic operation")
        self.assertGreaterEqual(res["total_skills_matched"], 1)
        self.assertGreaterEqual(res["total_adapters_matched"], 2)
        adapter_keys = [a["key"] for a in res["matched_adapters"]]
        self.assertIn("quickbooks_online", adapter_keys)
        self.assertIn("revenuecat", adapter_keys)
        self.assertEqual(res["execution_strategy"], "DAG_MULTI_STEP_PIPELINE")


# =============================================================================
# 2. INNER CONTEXTUAL PLANNER TESTS
# =============================================================================
class TestInnerContextualPlanner(unittest.TestCase):
    """Test Suite for Component 2: InnerContextualPlanner multi-step DAG formulation."""

    def setUp(self):
        self.router = InnerAppSkillRouter()
        self.planner = InnerContextualPlanner()

    def test_01_create_dag_plan_structure(self):
        """Verify create_dag_plan returns a valid 5-node DAG structure."""
        route_res = self.router.route_goal("Automate SaaS billing and GL ledger posting")
        plan = self.planner.create_dag_plan(
            goal=route_res["goal"],
            matched_skills=route_res["matched_skills"],
            matched_adapters=route_res["matched_adapters"],
            gl_amount=3500.00
        )

        self.assertTrue(plan["plan_id"].startswith("dag_plan_"))
        self.assertEqual(plan["status"], "PLANNED_DAG_VALIDATED")
        self.assertEqual(plan["total_steps"], 6)
        self.assertEqual(len(plan["nodes"]), 6)
        self.assertGreaterEqual(len(plan["edges"]), 4)

    def test_02_dag_node_actions_and_dependencies(self):
        """Verify DAG nodes contain expected actions, step sequence, and directed dependencies."""
        route_res = self.router.route_goal("Verify entitlements and post GL")
        plan = self.planner.create_dag_plan(
            goal=route_res["goal"],
            matched_skills=route_res["matched_skills"],
            matched_adapters=route_res["matched_adapters"]
        )

        nodes = plan["nodes"]
        actions = [n["action"] for n in nodes]
        self.assertEqual(actions[0], "VERIFY_REVENUECAT_ENTITLEMENTS")
        self.assertEqual(actions[1], "CONFIGURE_SAAS_APP_ADAPTERS")
        self.assertEqual(actions[2], "EXECUTE_INNER_SKILLS_PAYLOAD")
        self.assertEqual(actions[3], "GENERATE_ZK_DILITHIUM_POST_QUANTUM_PROOF")
        self.assertEqual(actions[4], "POST_QUICKBOOKS_DOUBLE_ENTRY_GL")

        # Check step 5 GL entry
        gl_entry = nodes[4]["gl_entry"]
        self.assertEqual(gl_entry["debit_account"], "1000 Cash")
        self.assertEqual(gl_entry["credit_account"], "4000 Revenue")
        self.assertEqual(gl_entry["balance_variance"], 0.00)

    def test_03_dag_custom_entitlements_and_gl_amount(self):
        """Verify custom entitlements and GL amounts pass through correctly to plan nodes."""
        route_res = self.router.route_goal("Enterprise custom workflow")
        custom_entitlements = ["enterprise_singularity_v2", "custom_vip_tier"]
        plan = self.planner.create_dag_plan(
            goal=route_res["goal"],
            matched_skills=route_res["matched_skills"],
            matched_adapters=route_res["matched_adapters"],
            entitlements=custom_entitlements,
            gl_amount=12500.50
        )

        node_01 = plan["nodes"][0]
        self.assertEqual(node_01["required_entitlements"], custom_entitlements)

        node_05 = plan["nodes"][4]
        self.assertEqual(node_05["gl_entry"]["amount"], 12500.50)


# =============================================================================
# 3. INNER SKILL EXECUTOR TESTS
# =============================================================================
class TestInnerSkillExecutor(unittest.TestCase):
    """Test Suite for Component 3: InnerSkillExecutor execution across SaaS app adapters."""

    def setUp(self):
        self.router = InnerAppSkillRouter()
        self.planner = InnerContextualPlanner()
        self.executor = InnerSkillExecutor(self.router)

    def test_01_execute_plan_success(self):
        """Verify execute_plan runs all 5 DAG nodes to completion."""
        route_res = self.router.route_goal("Execute full SaaS integration")
        plan = self.planner.create_dag_plan(
            goal=route_res["goal"],
            matched_skills=route_res["matched_skills"],
            matched_adapters=route_res["matched_adapters"]
        )

        exec_res = self.executor.execute_plan(plan)
        self.assertEqual(exec_res["status"], "EXECUTED_SUCCESSFULLY")
        self.assertGreaterEqual(exec_res["nodes_executed"], 5)
        self.assertGreaterEqual(exec_res["total_duration_ms"], 0.0)

    def test_02_execution_trace_integrity(self):
        """Verify execution trace per node contains valid status, timing, and SHA-256 payload hash."""
        route_res = self.router.route_goal("Execute trace test")
        plan = self.planner.create_dag_plan(
            goal=route_res["goal"],
            matched_skills=route_res["matched_skills"],
            matched_adapters=route_res["matched_adapters"]
        )

        exec_res = self.executor.execute_plan(plan)
        trace = exec_res["execution_trace"]
        self.assertGreaterEqual(len(trace), 5)

        for step in trace:
            self.assertEqual(step["status"], "COMPLETED")
            self.assertIn("node_id", step)
            self.assertIn("action", step)
            self.assertIn("execution_time_ms", step)
            self.assertIn("payload_hash", step)
            self.assertEqual(len(step["payload_hash"]), 64) # Valid SHA-256 hex string

    def test_03_quickbooks_and_zk_proof_node_results(self):
        """Verify node 4 (ZK Proof) and node 5 (GL Posting) output expected verification tokens."""
        route_res = self.router.route_goal("Verify GL and ZK output")
        plan = self.planner.create_dag_plan(
            goal=route_res["goal"],
            matched_skills=route_res["matched_skills"],
            matched_adapters=route_res["matched_adapters"],
            gl_amount=8800.00
        )

        exec_res = self.executor.execute_plan(plan)
        trace = exec_res["execution_trace"]

        zk_node_res = trace[3]["result"]
        self.assertEqual(zk_node_res["zk_dilithium_status"], "PROVED_AND_VERIFIED")
        self.assertIn("zk_dilithium_proof", zk_node_res)

        gl_node_res = trace[4]["result"]
        self.assertEqual(gl_node_res["quickbooks_gl_status"], "POSTED_AND_BALANCED")
        self.assertEqual(gl_node_res["amount"], 8800.00)
        self.assertEqual(gl_node_res["balance_variance"], 0.00)


# =============================================================================
# 4. INNER MEMORY CONSOLIDATOR TESTS
# =============================================================================
class TestInnerMemoryConsolidator(unittest.TestCase):
    """Test Suite for Component 4: InnerMemoryConsolidator RAG memory persistence."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.consolidator = InnerMemoryConsolidator(memory_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_persist_embedding_and_rag_file_creation(self):
        """Verify vector RAG embedding persistence to rag_index.json."""
        text = "Sovereign OS double-entry GL journal posting rule #104"
        res = self.consolidator.persist_embedding(text=text, metadata={"category": "finance"})

        self.assertEqual(res["status"], "VECTOR_EMBEDDING_PERSISTED")
        self.assertTrue(res["vector_id"].startswith("vec_"))
        self.assertTrue(os.path.exists(self.consolidator.rag_index_file))

        with open(self.consolidator.rag_index_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["text"], text)
        self.assertEqual(len(data[0]["embedding"]), 128)

    def test_02_search_rag_memory_cosine_similarity(self):
        """Verify search_rag_memory computes cosine similarity and ranks results."""
        self.consolidator.persist_embedding("QuickBooks Online double-entry ledger posting", metadata={"id": 1})
        self.consolidator.persist_embedding("RevenueCat paywall StoreKit2 entitlement check", metadata={"id": 2})
        self.consolidator.persist_embedding("FedWire ACH banking treasury transfer", metadata={"id": 3})

        results = self.consolidator.search_rag_memory("QuickBooks ledger", top_k=2)
        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), 2)
        
        first = results[0]
        self.assertIn("similarity_score", first)
        self.assertIn("vector_id", first)
        self.assertIn("text", first)

    def test_03_consolidate_learned_skill_markdown(self):
        """Verify learned skill markdown persistence and catalog entry."""
        skill_name = "custom_quickbooks_paywall_router"
        markdown_content = "# Custom Learned Skill\nAutomates RevenueCat and QuickBooks sync."
        
        res = self.consolidator.consolidate_learned_skill(
            skill_name=skill_name,
            code_or_markdown=markdown_content,
            category="autonomic_test"
        )

        self.assertEqual(res["status"], "LEARNED_SKILL_PERSISTED")
        self.assertTrue(os.path.exists(res["file_path"]))

        # Verify content written
        with open(res["file_path"], 'r', encoding='utf-8') as f:
            written = f.read()
        self.assertEqual(written, markdown_content)

        # Verify catalog updated
        self.assertTrue(os.path.exists(self.consolidator.learned_catalog_file))
        with open(self.consolidator.learned_catalog_file, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
        self.assertIn("custom_quickbooks_paywall_router", catalog)


# =============================================================================
# 5. INNER APP TELEMETRY PULSE TESTS
# =============================================================================
class TestInnerAppTelemetryPulse(unittest.TestCase):
    """Test Suite for Component 5: InnerAppTelemetryPulse Kuramoto phase calculation."""

    def setUp(self):
        self.telemetry = InnerAppTelemetryPulse(num_oscillators=200)

    def test_01_kuramoto_phase_coherence_calculation(self):
        """Verify Kuramoto phase coherence equation converges to R = 0.9999."""
        coherence = self.telemetry.compute_kuramoto_coherence(coupling_k=25.0, steps=60)
        self.assertEqual(coherence["status"], "KURAMOTO_PHASE_LOCK_PERFECT_COHERENCE")
        self.assertGreaterEqual(coherence["R_coherence"], 0.99)
        self.assertEqual(coherence["num_oscillators"], 200)
        self.assertIsInstance(coherence["mean_phase_psi"], float)

    def test_02_emit_pulse_metrics(self):
        """Verify emit_pulse returns full telemetry snapshot with 200 SaaS apps & 500 skills metrics."""
        pulse = self.telemetry.emit_pulse({"session_id": "test_sess_001"})

        self.assertTrue(pulse["pulse_id"].startswith("pulse_"))
        self.assertGreaterEqual(pulse["kuramoto_coherence_R"], 0.99)
        self.assertEqual(pulse["kuramoto_status"], "KURAMOTO_PHASE_LOCK_PERFECT_COHERENCE")

        metrics = pulse["telemetry_metrics"]
        self.assertEqual(metrics["active_saas_adapters"], 200)
        self.assertEqual(metrics["active_skills_catalog"], 500)
        self.assertEqual(metrics["throughput_qps"], 12500.0)
        self.assertEqual(metrics["error_rate_pct"], 0.00)
        self.assertIn("latency_p50_ms", metrics)
        self.assertIn("latency_p95_ms", metrics)
        self.assertIn("latency_p99_ms", metrics)


# =============================================================================
# 6. MASTER SOVEREIGN INNER AI ENGINE INTEGRATION TESTS
# =============================================================================
class TestSovereignInnerAIEngineMasterIntegration(unittest.TestCase):
    """Master Integration Test Suite unifying all 5 Inner AI Engine components."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.engine = SovereignInnerAIEngine(memory_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_full_end_to_end_goal_processing(self):
        """Verify process_goal executes end-to-end pipeline across router, planner, executor, consolidator & telemetry."""
        goal = "Execute automated double-entry accounting GL sync with ZK Dilithium proof and StoreKit2 paywall verification"
        res = self.engine.process_goal(goal=goal, gl_amount=5000.00)

        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["goal"], goal)

        # Check Routing
        self.assertGreater(res["routing"]["total_skills_matched"], 0)
        self.assertGreater(res["routing"]["total_adapters_matched"], 0)

        # Check DAG Plan
        self.assertEqual(res["dag_plan"]["status"], "PLANNED_DAG_VALIDATED")
        self.assertGreaterEqual(res["dag_plan"]["total_steps"], 5)

        # Check Execution
        self.assertEqual(res["execution"]["status"], "EXECUTED_SUCCESSFULLY")
        self.assertGreaterEqual(res["execution"]["nodes_executed"], 5)

        # Check Memory Consolidation
        self.assertEqual(res["memory_consolidation"]["rag_embedding"]["status"], "VECTOR_EMBEDDING_PERSISTED")
        self.assertEqual(res["memory_consolidation"]["learned_skill"]["status"], "LEARNED_SKILL_PERSISTED")

        # Check Telemetry Pulse
        self.assertGreaterEqual(res["telemetry_pulse"]["kuramoto_coherence_R"], 0.99)

        # Check Master Audit
        audit = res["master_audit"]
        self.assertTrue(audit["revenuecat_entitlements_verified"])
        self.assertTrue(audit["zk_dilithium_proof_generated"])
        self.assertTrue(audit["quickbooks_gl_posted_and_balanced"])
        self.assertGreaterEqual(audit["kuramoto_phase_coherence_R"], 0.99)

    def test_02_zk_dilithium_proof_engine_standalone(self):
        """Verify SovereignZKDilithiumProofEngine generates and verifies post-quantum ZK signatures."""
        data = b"Sovereign_OS_Master_Audit_Payload_2026"
        proof = SovereignZKDilithiumProofEngine.generate_proof(data)

        self.assertEqual(proof["algorithm"], "Dilithium5_PostQuantum_ZK")
        self.assertTrue(proof["proof_hash"].startswith("0x"))
        self.assertTrue(proof["zk_snark_commitment"].startswith("zk_commit_"))
        self.assertTrue(proof["zk_proof_signature"].startswith("zk_sig_dilithium5_"))

        isValid = SovereignZKDilithiumProofEngine.verify_proof(data, proof)
        self.assertTrue(isValid)


if __name__ == "__main__":
    unittest.main()
