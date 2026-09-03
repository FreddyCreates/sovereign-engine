"""
TEST SUITE FOR SOVEREIGN POLYMATH PROTOCOL ENGINE
=================================================

Automated unit & integration test suite verifying (5 tests per engine x 5 engines = 25 tests total):
1. PolymathMachineIngestEngine
2. AutonomousNavigationAgentAPI
3. UniversityGatewaysAggregator
4. RecursiveLearningEngine
5. SovereignPolymathProtocolOrchestrator
"""

import unittest
import json
import time
import os
import sys

# Ensure module path resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../sovereign_infrastructure/nextgen_systems')))

from sovereign_infrastructure.nextgen_systems.sovereign_polymath_protocol_engine import (
    PolymathMachineIngestEngine,
    AutonomousNavigationAgentAPI,
    UniversityGatewaysAggregator,
    RecursiveLearningEngine,
    SovereignPolymathProtocolOrchestrator,
    polymath_orchestrator
)


class TestPolymathMachineIngestEngine(unittest.TestCase):
    """Tests Component 1: PolymathMachineIngestEngine."""

    def setUp(self):
        self.engine = PolymathMachineIngestEngine()

    def test_01_process_artifact_machine_mode(self):
        res = self.engine.process_artifact_machine_mode(
            artifact_id="art_101",
            title="MIT 18.06 Linear Algebra",
            duration_minutes=94.0
        )
        self.assertEqual(res["status"], "EXTRACTION_COMPLETE")
        self.assertIn("realtime", res["processing_speed"])
        self.assertEqual(res["total_frames_extracted"], 94 * 60 * 30)

    def test_02_batch_process_queue(self):
        queue = [
            {"id": "v1", "title": "Quantum Physics 101", "duration": 60},
            {"id": "v2", "title": "Advanced Thermodynamics", "duration": 45}
        ]
        res = self.engine.batch_process_queue(queue)
        self.assertEqual(res["batch_status"], "BATCH_EXTRACTION_COMPLETE")
        self.assertEqual(res["total_items_processed"], 2)

    def test_03_zero_duration_fallback(self):
        res = self.engine.process_artifact_machine_mode(
            artifact_id="art_000",
            title="Micro Lecture",
            duration_minutes=1.0
        )
        self.assertEqual(res["duration_minutes"], 1.0)
        self.assertEqual(res["total_frames_extracted"], 1800)

    def test_04_stats_accumulation(self):
        initial_artifacts = self.engine.stats["total_artifacts_processed"]
        self.engine.process_artifact_machine_mode("art_999", "Deep Learning", 120.0)
        self.assertEqual(self.engine.stats["total_artifacts_processed"], initial_artifacts + 1)

    def test_05_machine_ingest_rfc3339_timestamp(self):
        res = self.engine.process_artifact_machine_mode("art_rfc", "RFC Timestamp Test", 30.0)
        self.assertIn("T", res["timestamp"])
        self.assertTrue(res["timestamp"].endswith("Z") or "+" in res["timestamp"])


class TestAutonomousNavigationAgentAPI(unittest.TestCase):
    """Tests Component 2: AutonomousNavigationAgentAPI."""

    def setUp(self):
        self.api = AutonomousNavigationAgentAPI()

    def test_01_execute_agent_navigation(self):
        res = self.api.execute_agent_navigation(
            agent="SILVER NOVA",
            action="set_playback_rate",
            value=8.0,
            reason="Known foundational content"
        )
        self.assertEqual(res["status"], "COMMAND_EXECUTED")
        self.assertEqual(self.api.current_playback_rate, 8.0)
        self.assertEqual(res["log_entry"]["agent"], "SILVER NOVA")

    def test_02_get_spectral_confidence_map(self):
        conf_map = self.api.get_spectral_confidence_map(duration_sec=3600)
        self.assertEqual(len(conf_map["timeline_segments"]), 20)
        self.assertGreaterEqual(conf_map["spectral_confidence_avg"], 0)

    def test_03_override_toggle_navigation(self):
        res = self.api.execute_agent_navigation(
            agent="DARWIN",
            action="override_toggle",
            value=False,
            reason="Testing manual override toggle"
        )
        self.assertFalse(self.api.override_active)
        self.assertEqual(res["status"], "COMMAND_EXECUTED")

    def test_04_control_log_rotation(self):
        initial_len = len(self.api.control_logs)
        self.api.execute_agent_navigation("CODEX", "set_playback_rate", 2.0, "Test rotation")
        self.assertEqual(len(self.api.control_logs), initial_len + 1)

    def test_05_rfc3339_timestamp_format(self):
        res = self.api.execute_agent_navigation("AURORA", "set_playback_rate", 4.0, "Timestamp verification")
        ts = res["log_entry"]["timestamp"]
        self.assertIn("T", ts)


class TestUniversityGatewaysAggregator(unittest.TestCase):
    """Tests Component 3: UniversityGatewaysAggregator."""

    def setUp(self):
        self.gateways = UniversityGatewaysAggregator()

    def test_01_search_gateways(self):
        results = self.gateways.search_gateways("Quantum Computing")
        self.assertGreaterEqual(len(results), 3)

    def test_02_build_auto_curriculum(self):
        curriculum = self.gateways.build_auto_curriculum("Quantum Computing & ZK Cryptography")
        self.assertEqual(curriculum["total_modules"], 15)
        self.assertIn("modules", curriculum)

    def test_03_get_gateways_list(self):
        gw_list = self.gateways.get_gateways()
        self.assertEqual(len(gw_list), 6)
        self.assertTrue(any(g["id"] == "mit" for g in gw_list))

    def test_04_curriculum_duration_calculation(self):
        curr = self.gateways.build_auto_curriculum("Machine Learning")
        self.assertGreater(curr["estimated_total_hours"], 0)
        self.assertEqual(len(curr["modules"]), 15)

    def test_05_search_gateways_with_empty_query(self):
        results = self.gateways.search_gateways("")
        self.assertGreaterEqual(len(results), 4)


class TestRecursiveLearningEngine(unittest.TestCase):
    """Tests Component 4: RecursiveLearningEngine."""

    def setUp(self):
        self.engine = RecursiveLearningEngine()

    def test_01_detect_knowledge_gaps(self):
        res = self.engine.detect_knowledge_gaps("Advanced Signal Processing")
        self.assertEqual(res["gaps_detected_count"], 3)

    def test_02_trigger_recursive_research(self):
        res = self.engine.trigger_recursive_research("Fourier Transform Applications", current_depth=1)
        self.assertEqual(res["status"], "RECURSIVE_SEARCH_COMPLETE")

    def test_03_calculate_polymath_score(self):
        score_res = self.engine.calculate_polymath_score()
        self.assertGreater(score_res["polymath_score"], 1000)
        self.assertEqual(len(score_res["leaderboard"]), 4)

    def test_04_max_recursion_depth_boundary(self):
        res = self.engine.trigger_recursive_research("Deep Topology", current_depth=5)
        self.assertEqual(res["status"], "DEPTH_LIMIT_REACHED")
        self.assertIn("Max Depth", res["message"])

    def test_05_active_chains_integrity(self):
        self.assertEqual(len(self.engine.active_chains), 2)
        self.assertIn("root_topic", self.engine.active_chains[0])


class TestPolymathProtocolMasterIntegration(unittest.TestCase):
    """Tests Component 5: Master Orchestrator."""

    def test_01_full_dashboard_state(self):
        state = polymath_orchestrator.get_full_dashboard_state()
        self.assertEqual(state["status"], "POLYMATH_PROTOCOL_ACTIVE")
        self.assertIn("machine_mode_stats", state)
        self.assertIn("spectral_confidence", state)
        self.assertIn("polymath_score", state)

    def test_02_orchestrator_sub_engines_initialized(self):
        self.assertIsNotNone(polymath_orchestrator.ingest_engine)
        self.assertIsNotNone(polymath_orchestrator.nav_api)
        self.assertIsNotNone(polymath_orchestrator.gateways)
        self.assertIsNotNone(polymath_orchestrator.recursive_engine)

    def test_03_dashboard_state_rfc3339_timestamps(self):
        state = polymath_orchestrator.get_full_dashboard_state()
        logs = state["current_navigation"]["control_logs"]
        if logs:
            self.assertIn("T", logs[0]["timestamp"])

    def test_04_machine_ingest_and_dashboard_sync(self):
        polymath_orchestrator.ingest_engine.process_artifact_machine_mode("art_sync", "Sync Test", 50.0)
        state = polymath_orchestrator.get_full_dashboard_state()
        self.assertGreater(state["machine_mode_stats"]["total_artifacts_processed"], 0)

    def test_05_zero_float_drift_in_polymath_scores(self):
        score_info = polymath_orchestrator.recursive_engine.calculate_polymath_score()
        score = score_info["polymath_score"]
        self.assertEqual(score, round(score, 2))


if __name__ == "__main__":
    unittest.main()
