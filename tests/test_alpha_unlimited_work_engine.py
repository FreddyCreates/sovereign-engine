"""
Unit Tests for SOVEREIGN OS Alpha Unlimited Work Engine & AlphaAppWorkGenerator
"""

import pytest
from sovereign_infrastructure.nextgen_systems.alpha_unlimited_work_engine import (
    AlphaUnlimitedWorkEngine,
    AlphaAppWorkGenerator
)
from sovereign_infrastructure.nextgen_systems.full_saas_accounting_suite import GeneralLedgerEngine


def test_alpha_app_work_generator_init():
    generator = AlphaAppWorkGenerator()
    assert len(generator.apps) == 200
    assert len(generator.completed_tasks) == 0


def test_generate_work_for_individual_app():
    generator = AlphaAppWorkGenerator()
    
    # Test QuickBooks Online (Accounting & Tax)
    task1 = generator.generate_work_for_app("app_001")
    assert task1["status"] == "COMPLETED_SUCCESSFULLY"
    assert task1["app_name"] == "QuickBooks Online"
    assert task1["category"] == "Accounting & Tax"
    assert "reconciled" in task1["action_summary"]
    assert task1["execution_mode"] == "ALPHA_UNLIMITED_AUTONOMIC"
    assert task1["general_ledger_synced"] is True

    # Test Stripe Payments (Payment Gateways & Subscriptions)
    task2 = generator.generate_work_for_app("Stripe Payments")
    assert task2["status"] == "COMPLETED_SUCCESSFULLY"
    assert task2["app_name"] == "Stripe Payments"
    assert task2["category"] == "Payment Gateways & Subscriptions"
    assert "StoreKit 2" in task2["action_summary"]

    # Test OpenAI GPT-4o (AI & Neural Engines)
    task3 = generator.generate_work_for_app("OpenAI GPT-4o")
    assert task3["status"] == "COMPLETED_SUCCESSFULLY"
    assert task3["category"] == "AI & Neural Engines"

    assert len(generator.completed_tasks) == 3


def test_generate_work_with_gl_integration():
    gl = GeneralLedgerEngine()
    generator = AlphaAppWorkGenerator(gl_engine=gl)
    
    task = generator.generate_work_for_app("app_001")
    assert task["journal_entry_id"] is not None
    
    tb = gl.generate_trial_balance()
    assert tb["is_balanced"] is True


def test_generate_work_for_all_200_apps():
    generator = AlphaAppWorkGenerator()
    res = generator.generate_work_for_all_200_apps(batch_size=50, parallel=True)

    assert res["total_apps_processed"] == 200
    assert res["total_tasks_completed"] == 200
    assert res["execution_mode"] == "ALPHA_UNLIMITED_PARALLEL"
    assert res["general_ledger_variance"] == 0.00
    assert res["status"] == "ALL_200_APPS_AUTONOMIC_WORK_COMPLETED"
    assert len(res["category_breakdown"]) == 10
    assert sum(res["category_breakdown"].values()) == 200


def test_alpha_unlimited_work_engine_cycles():
    gl = GeneralLedgerEngine()
    engine = AlphaUnlimitedWorkEngine(gl_engine=gl, max_workers=20)

    report = engine.execute_unlimited_work_cycle(num_cycles=2)
    assert report["cycles_executed"] == 2
    assert report["total_apps_processed"] == 400
    assert report["total_tasks_completed"] == 400
    assert report["general_ledger_variance"] == 0.00
    assert report["status"] == "UNLIMITED_WORK_CYCLE_SUCCESSFUL"
    assert report["throughput_tasks_per_sec"] > 0


def test_alpha_unlimited_work_engine_audit():
    engine = AlphaUnlimitedWorkEngine()
    audit = engine.run_alpha_audit()

    assert audit["engine_name"] == "SOVEREIGN OS Alpha Unlimited Work Engine"
    assert audit["capacity"] == "UNLIMITED_PARALLEL_EXECUTION"
    assert audit["total_supported_apps"] == 200
    assert audit["status"] == "ALPHA_ENGINE_ONLINE_OPTIMAL"
    assert audit["substrate_status"]["XFIN"] == "HEALTHY"


def test_worker_pool_scaling_and_telemetry():
    engine = AlphaUnlimitedWorkEngine(max_workers=10)
    scale_res = engine.scale_worker_pool(100)
    assert scale_res["max_workers"] == 100

    telemetry = engine.stream_autonomic_work_telemetry()
    assert telemetry["active_max_workers"] == 100
    assert telemetry["status"] == "TELEMETRY_STREAM_HEALTHY"
    assert telemetry["gl_variance_usd"] == 0.00


def test_work_history_filtering_and_clearing():
    generator = AlphaAppWorkGenerator()
    generator.generate_work_for_app("QuickBooks Online")
    generator.generate_work_for_app("Stripe Payments")

    acct_tasks = generator.get_work_history(category="Accounting & Tax")
    assert len(acct_tasks) == 1
    assert acct_tasks[0]["app_name"] == "QuickBooks Online"

    breakdown = generator.get_category_work_breakdown()
    assert breakdown["Accounting & Tax"] == 1
    assert breakdown["Payment Gateways & Subscriptions"] == 1

    generator.clear_history()
    assert len(generator.completed_tasks) == 0
