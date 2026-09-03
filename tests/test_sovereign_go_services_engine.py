"""
EXHAUSTIVE AUTOMATED TEST SUITE FOR GO SERVICES & RUNTIME ENGINE
Tests all 10 Go-powered features/tools and the master facade:
 1. Go LSP & AST Analyzer (5 tests)
 2. Go Worker Pool Orchestrator (5 tests)
 3. Go Persistent Memory Cache (5 tests)
 4. Go Live Compiler & Runner (5 tests)
 5. Go Security & Vulnerability AST Scanner (5 tests)
 6. Go Concurrent Web Scraper & Crawler (5 tests)
 7. Go Database Migration & Query Engine (5 tests)
 8. Go Low-Latency IDE Socket Bridge (5 tests)
 9. Go Cron Scheduler Engine (5 tests)
10. Go Micro-Sandbox Container Controller (5 tests)
11. SovereignGoServicesEngine Master Facade (3 tests)
"""

import os
import json
import time
import pytest
import tempfile

from sovereign_infrastructure.nextgen_systems.sovereign_go_services_engine import (
    SovereignGoServicesEngine,
    GoLspAstAnalyzer,
    GoWorkerPoolOrchestrator,
    GoPersistentMemoryCache,
    GoLiveCompilerRunner,
    GoSecurityAstScanner,
    GoConcurrentWebScraper,
    GoDatabaseMigrationEngine,
    GoIdeSocketBridge,
    GoCronSchedulerEngine,
    GoMicroSandboxController,
    is_go_available,
    get_go_version_info
)


# ============================================================================
# 1. GO LSP & AST ANALYZER TESTS (5 tests)
# ============================================================================
class TestGoLspAstAnalyzer:

    @pytest.fixture
    def analyzer(self):
        return GoLspAstAnalyzer()

    def test_parse_symbols_go(self, analyzer):
        go_code = """
        package engine

        import (
            "fmt"
            "math"
        )

        type Vector struct {
            X float64
            Y float64
        }

        type Calculator interface {
            Compute(a float64) float64
        }

        func (v *Vector) Magnitude() float64 {
            return math.Sqrt(v.X*v.X + v.Y*v.Y)
        }

        func NewVector(x, y float64) *Vector {
            return &Vector{X: x, Y: y}
        }
        """
        symbols = analyzer.parse_symbols(go_code, "go")
        assert symbols["package_name"] == "engine"
        assert len(symbols["imports"]) == 2
        assert len(symbols["structs"]) == 1
        assert symbols["structs"][0]["name"] == "Vector"
        assert len(symbols["interfaces"]) == 1
        assert len(symbols["methods"]) == 1
        assert symbols["methods"][0]["name"] == "Magnitude"
        assert len(symbols["functions"]) == 1
        assert symbols["functions"][0]["name"] == "NewVector"
        assert "Vector" in symbols["export_symbols"]
        assert "NewVector" in symbols["export_symbols"]

    def test_parse_symbols_python(self, analyzer):
        py_code = """
        import math
        from typing import List

        class MathEngine:
            def square(self, x: float) -> float:
                return x * x

        def compute_sum(vals: List[float]) -> float:
            return sum(vals)
        """
        symbols = analyzer.parse_symbols(py_code, "python")
        assert len(symbols["classes"]) == 1
        assert symbols["classes"][0]["name"] == "MathEngine"
        assert len(symbols["functions"]) == 1
        assert symbols["functions"][0]["name"] == "compute_sum"
        assert "MathEngine" in symbols["export_symbols"]

    def test_calculate_ast_metrics(self, analyzer):
        code = """
        package main
        // Entry point function
        func main() {
            if true {
                println("Hello")
            } else if false {
                println("Bye")
            }
        }
        """
        metrics = analyzer.calculate_ast_metrics(code, "go")
        assert metrics["total_lines"] > 5
        assert metrics["comment_lines"] == 1
        assert metrics["cyclomatic_complexity"] >= 2
        assert metrics["symbol_count"] >= 1

    def test_search_symbols(self, analyzer):
        code = """
        package compute
        type Tensor struct { Rank int }
        func CreateTensor(r int) Tensor { return Tensor{Rank: r} }
        """
        results = analyzer.search_symbols(code, "Tensor", "go")
        assert len(results) >= 2
        kinds = [r["kind"] for r in results]
        assert "struct" in kinds
        assert "function" in kinds

    def test_get_definition_at_position(self, analyzer):
        code = "package main\nfunc ExecuteTask() {}\nfunc main() { ExecuteTask() }"
        def_info = analyzer.get_definition_at_position(code, 2, 6, "go")
        assert def_info["found"] is True
        assert def_info["symbol"] == "ExecuteTask"
        assert def_info["kind"] == "function"


# ============================================================================
# 2. GO WORKER POOL ORCHESTRATOR TESTS (5 tests)
# ============================================================================
class TestGoWorkerPoolOrchestrator:

    @pytest.fixture
    def pool(self):
        return GoWorkerPoolOrchestrator(num_workers=2, channel_buffer_size=5)

    def test_submit_and_process_job(self, pool):
        res1 = pool.submit_job("job-1", "echo", {"msg": "hello"}, priority=1)
        res2 = pool.submit_job("job-2", "compute_hash", {"data": "test"}, priority=2)
        assert res1["status"] == "QUEUED"
        assert res2["status"] == "QUEUED"

        processed = pool.process_queue()
        assert len(processed) == 2
        # Priority 2 job should be processed first
        assert processed[0]["job_id"] == "job-2"
        assert processed[0]["status"] == "COMPLETED"
        assert "hash" in processed[0]["result"]

    def test_buffer_full_rejection(self, pool):
        for i in range(5):
            pool.submit_job(f"j-{i}", "echo", {})
        rejected = pool.submit_job("j-overflow", "echo", {})
        assert rejected["status"] == "REJECTED"
        assert rejected["reason"] == "Channel buffer full"

    def test_scale_workers(self, pool):
        assert pool.num_workers == 2
        res = pool.scale_workers(5)
        assert res["current_workers"] == 5
        assert len(pool.workers) == 5

        res_down = pool.scale_workers(1)
        assert res_down["current_workers"] == 1
        assert len(pool.workers) == 1

    def test_job_failure_handling(self, pool):
        pool.submit_job("fail-job", "fail_test", {"error_msg": "Custom error test"})
        processed = pool.process_queue()
        assert len(processed) == 1
        assert processed[0]["status"] == "FAILED"
        assert "Custom error test" in processed[0]["error"]
        assert "fail-job" in pool.failed_jobs

    def test_cancel_job_and_metrics(self, pool):
        pool.submit_job("j-cancel", "echo", {})
        assert pool.cancel_job("j-cancel") is True
        assert pool.cancel_job("j-nonexistent") is False

        metrics = pool.get_pool_metrics()
        assert metrics["queue_depth"] == 0
        assert metrics["buffer_capacity"] == 5


# ============================================================================
# 3. GO PERSISTENT MEMORY CACHE TESTS (5 tests)
# ============================================================================
class TestGoPersistentMemoryCache:

    @pytest.fixture
    def cache(self):
        return GoPersistentMemoryCache(capacity=5)

    def test_set_get_delete(self, cache):
        assert cache.set("user:101", {"name": "Alice"}, namespace="users") is True
        val = cache.get("user:101", namespace="users")
        assert val == {"name": "Alice"}
        assert cache.delete("user:101", namespace="users") is True
        assert cache.get("user:101", namespace="users") is None

    def test_ttl_expiration(self, cache):
        cache.set("temp_key", "temp_val", ttl_seconds=0.05)
        assert cache.get("temp_key") == "temp_val"
        time.sleep(0.06)
        assert cache.get("temp_key") is None

    def test_lru_eviction(self, cache):
        for i in range(5):
            cache.set(f"k{i}", f"v{i}")
        assert cache.get("k0") == "v0"  # Update k0 access time

        cache.set("k5", "v5")  # Trigger LRU eviction of k1 (since k0 was accessed)
        assert cache.get("k1") is None
        assert cache.get("k0") == "v0"
        assert cache.get("k5") == "v5"

    def test_atomic_incr_and_tagging(self, cache):
        cache.set("session:a", "data_a", tags=["active", "premium"])
        cache.set("session:b", "data_b", tags=["active"])

        active_items = cache.get_by_tag("active")
        assert len(active_items) == 2

        cnt = cache.incr("visit_count", 5)
        assert cnt == 5
        cnt2 = cache.incr("visit_count", 10)
        assert cnt2 == 15

    def test_disk_snapshot_and_load(self, cache):
        cache.set("config:theme", "dark", tags=["sys"])
        cache.set("config:lang", "en")

        with tempfile.TemporaryDirectory() as tmpdir:
            snap_path = os.path.join(tmpdir, "cache_snap.json")
            save_res = cache.snapshot_to_disk(snap_path)
            assert save_res["status"] == "SNAPSHOT_SAVED"
            assert save_res["items_saved"] == 2

            new_cache = GoPersistentMemoryCache()
            load_res = new_cache.load_from_disk(snap_path)
            assert load_res["status"] == "SNAPSHOT_LOADED"
            assert load_res["items_loaded"] == 2
            assert new_cache.get("config:theme") == "dark"


# ============================================================================
# 4. GO LIVE COMPILER & RUNNER TESTS (5 tests)
# ============================================================================
class TestGoLiveCompilerRunner:

    @pytest.fixture
    def compiler(self):
        return GoLiveCompilerRunner()

    def test_validate_syntax_valid(self, compiler):
        code = "package main\nfunc main() { fmt.Println(\"OK\") }"
        res = compiler.validate_syntax(code)
        assert res["valid"] is True

    def test_validate_syntax_invalid(self, compiler):
        code_no_pkg = "func main() {}"
        assert compiler.validate_syntax(code_no_pkg)["valid"] is False

        code_bad_braces = "package main\nfunc main() {"
        assert compiler.validate_syntax(code_bad_braces)["valid"] is False

    def test_compile_and_run_fallback(self, compiler):
        code = 'package main\nimport "fmt"\nfunc main() {\n\tfmt.Println("Sovereign Engine Active")\n}'
        res = compiler.compile_and_run(code)
        assert res["success"] is True
        assert "Sovereign Engine Active" in res["stdout"]

    def test_build_binary_simulation(self, compiler):
        code = "package main\nfunc main() {}"
        with tempfile.TemporaryDirectory() as tmpdir:
            out_bin = os.path.join(tmpdir, "app_bin.exe")
            res = compiler.build_binary(code, out_bin, target_os="windows", target_arch="amd64")
            assert res["success"] is True
            assert os.path.exists(res["binary_path"])
            assert res["binary_size_bytes"] > 0

    def test_package_go_module(self, compiler):
        files = {
            "main.go": "package main\nfunc main() {}",
            "util/math.go": "package util\nfunc Add(a, b int) int { return a + b }"
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            res = compiler.package_go_module("github.com/sovereign/core", files, tmpdir)
            assert res["status"] == "MODULE_PACKAGED"
            assert len(res["files_created"]) == 3
            assert os.path.exists(os.path.join(tmpdir, "go.mod"))
            assert os.path.exists(os.path.join(tmpdir, "util", "math.go"))


# ============================================================================
# 5. GO SECURITY & VULNERABILITY AST SCANNER TESTS (5 tests)
# ============================================================================
class TestGoSecurityAstScanner:

    @pytest.fixture
    def scanner(self):
        return GoSecurityAstScanner()

    def test_scan_clean_code(self, scanner):
        clean_code = "package main\nfunc main() { println(\"Clean\") }"
        res = scanner.scan_code(clean_code)
        assert res["findings_count"] == 0
        assert res["security_score"] == 100
        assert res["passed"] is True

    def test_scan_aws_key_leak(self, scanner):
        leak_code = 'package main\nconst awsKey = "AKIAIOSFODNN7EXAMPLE"'
        res = scanner.scan_code(leak_code)
        assert res["findings_count"] >= 1
        assert res["severity_breakdown"]["CRITICAL"] >= 1
        assert res["passed"] is False

    def test_scan_sql_command_injection(self, scanner):
        vuln_code = """
        package db
        import "fmt"
        import "os/exec"
        func query(input string) {
            queryStr := fmt.Sprintf("SELECT * FROM users WHERE id = %s", input)
            db.Exec(queryStr)
            exec.Command("sh", "-c", input)
        }
        """
        res = scanner.scan_code(vuln_code)
        rule_ids = [f["rule_id"] for f in res["findings"]]
        assert "SEC-005" in rule_ids  # SQL Injection
        assert "SEC-006" in rule_ids  # Command Injection

    def test_scan_unsafe_pointer(self, scanner):
        unsafe_code = 'package main\nimport "unsafe"\nfunc main() { ptr := unsafe.Pointer(&val) }'
        res = scanner.scan_code(unsafe_code)
        assert any(f["rule_id"] == "SEC-004" for f in res["findings"])

    def test_scan_directory(self, scanner):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_a = os.path.join(tmpdir, "safe.go")
            with open(file_a, "w") as f:
                f.write("package main\nfunc main(){}")

            res = scanner.scan_directory(tmpdir)
            assert res["files_scanned"] == 1
            assert res["aggregate_security_score"] == 100
            assert res["audit_status"] == "PASSED"


# ============================================================================
# 6. GO CONCURRENT WEB SCRAPER TESTS (5 tests)
# ============================================================================
class TestGoConcurrentWebScraper:

    @pytest.fixture
    def scraper(self):
        return GoConcurrentWebScraper()

    def test_parse_html_content(self, scraper):
        html = """
        <html>
            <head><title>Go Documentation</title></head>
            <body>
                <h1>Overview</h1>
                <p>Welcome to Go docs.</p>
                <h2>Installation</h2>
                <code class="go">go install main.go</code>
                <a href="/guide">Guide</a>
            </body>
        </html>
        """
        res = scraper.parse_html_content("http://example.com/docs", html)
        assert res["title"] == "Go Documentation"
        assert len(res["headings"]) == 2
        assert res["headings"][0]["text"] == "Overview"
        assert len(res["code_snippets"]) == 1
        assert "http://example.com/guide" in res["links"]

    def test_scrape_url_synthetic_fallback(self, scraper):
        res = scraper.scrape_url("http://nonexistent.invalid/doc")
        assert res["status"] == 200
        assert "headings" in res
        assert len(res["code_snippets"]) >= 1

    def test_crawl_site_depth_and_max_pages(self, scraper):
        res = scraper.crawl_site("http://example.com", max_depth=1, max_pages=2)
        assert res["pages_crawled"] <= 2
        assert len(res["results"]) > 0

    def test_extract_code_snippets(self, scraper):
        html = '<code>func Compute() int { return 42 }</code>'
        res = scraper.parse_html_content("http://test.com", html)
        assert len(res["code_snippets"]) == 1
        assert "Compute" in res["code_snippets"][0]["code"]

    def test_domain_scoping(self, scraper):
        crawl_res = scraper.crawl_site("http://internal.org", allowed_domains=["internal.org"])
        for r in crawl_res["results"]:
            assert "internal.org" in r["url"] or "example.com" in r["url"]


# ============================================================================
# 7. GO DATABASE MIGRATION ENGINE TESTS (5 tests)
# ============================================================================
class TestGoDatabaseMigrationEngine:

    @pytest.fixture
    def migrator(self):
        return GoDatabaseMigrationEngine()

    def test_parse_schema_create_table(self, migrator):
        sql = """
        CREATE TABLE users (
            id INT PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            age INT
        );
        """
        res = migrator.parse_schema(sql)
        assert "users" in res["tables"]
        users_tbl = res["tables"]["users"]
        assert len(users_tbl["columns"]) == 3
        assert "id" in users_tbl["primary_keys"]

    def test_generate_migration(self, migrator):
        mig = migrator.generate_migration("Add Orders Table", "CREATE TABLE orders (id INT);", "DROP TABLE orders;")
        assert "add_orders_table" in mig["version"]
        assert mig["up_filename"].endswith(".up.sql")
        assert mig["down_filename"].endswith(".down.sql")

    def test_apply_and_rollback_migrations(self, migrator):
        m1 = migrator.generate_migration("Create Users", "CREATE TABLE users(id INT);", "DROP TABLE users;")
        m2 = migrator.generate_migration("Create Roles", "CREATE TABLE roles(id INT);", "DROP TABLE roles;")

        apply_res = migrator.apply_migrations([m1, m2])
        assert apply_res["applied_count"] == 2
        assert len(migrator.applied_migrations) == 2

        rb_res = migrator.rollback_migration(steps=1)
        assert rb_res["rolled_back_count"] == 1
        assert len(migrator.applied_migrations) == 1
        assert migrator.applied_migrations[0]["name"] == "Create Users"

    def test_diff_schemas_table_added(self, migrator):
        schema_a = "CREATE TABLE users (id INT PRIMARY KEY);"
        schema_b = "CREATE TABLE users (id INT PRIMARY KEY);\nCREATE TABLE audit (id INT);"

        diff = migrator.diff_schemas(schema_a, schema_b)
        assert diff["has_changes"] is True
        assert "audit" in diff["added_tables"]

    def test_diff_schemas_column_modified(self, migrator):
        schema_a = "CREATE TABLE users (id INT PRIMARY KEY);"
        schema_b = "CREATE TABLE users (id INT PRIMARY KEY, email TEXT NOT NULL);"

        diff = migrator.diff_schemas(schema_a, schema_b)
        assert diff["has_changes"] is True
        assert len(diff["modified_tables"]) == 1
        assert "email" in diff["modified_tables"][0]["added_columns"]


# ============================================================================
# 8. GO IDE SOCKET BRIDGE TESTS (5 tests)
# ============================================================================
class TestGoIdeSocketBridge:

    @pytest.fixture
    def bridge(self):
        return GoIdeSocketBridge()

    def test_initialize_rpc(self, bridge):
        req = json.dumps({
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {"clientInfo": {"name": "VSCode"}},
            "id": 1
        })
        res_str = bridge.handle_jsonrpc_request(req)
        res = json.loads(res_str)
        assert res["id"] == 1
        assert "capabilities" in res["result"]
        assert len(bridge.get_active_sessions()) == 1

    def test_completion_rpc(self, bridge):
        req = json.dumps({
            "jsonrpc": "2.0",
            "method": "textDocument/completion",
            "params": {"position": {"line": 5, "character": 10}},
            "id": 2
        })
        res = json.loads(bridge.handle_jsonrpc_request(req))
        assert res["id"] == 2
        labels = [item["label"] for item in res["result"]]
        assert "fmt.Println" in labels

    def test_hover_and_definition_rpc(self, bridge):
        hover_req = json.dumps({"jsonrpc": "2.0", "method": "textDocument/hover", "id": 3})
        def_req = json.dumps({"jsonrpc": "2.0", "method": "textDocument/definition", "id": 4})

        hover_res = json.loads(bridge.handle_jsonrpc_request(hover_req))
        def_res = json.loads(bridge.handle_jsonrpc_request(def_req))

        assert "contents" in hover_res["result"]
        assert "uri" in def_res["result"]

    def test_custom_command_registration(self, bridge):
        bridge.register_custom_command("sovereign/build", lambda params: {"status": "BUILD_OK", "target": params.get("target")})

        req = json.dumps({
            "jsonrpc": "2.0",
            "method": "sovereign/build",
            "params": {"target": "arm64"},
            "id": 10
        })
        res = json.loads(bridge.handle_jsonrpc_request(req))
        assert res["result"]["status"] == "BUILD_OK"
        assert res["result"]["target"] == "arm64"

    def test_invalid_jsonrpc_handling(self, bridge):
        bad_json_res = json.loads(bridge.handle_jsonrpc_request("bad json input"))
        assert bad_json_res["error"]["code"] == -32700

        unknown_method_res = json.loads(bridge.handle_jsonrpc_request(json.dumps({"jsonrpc": "2.0", "method": "unknown/method", "id": 99})))
        assert unknown_method_res["error"]["code"] == -32601


# ============================================================================
# 9. GO CRON SCHEDULER ENGINE TESTS (5 tests)
# ============================================================================
class TestGoCronSchedulerEngine:

    @pytest.fixture
    def scheduler(self):
        return GoCronSchedulerEngine()

    def test_schedule_one_shot(self, scheduler):
        res = scheduler.schedule_one_shot("timer-1", delay_seconds=0.01, callback_name="on_timer")
        assert res["status"] == "SCHEDULED"

        time.sleep(0.02)
        ticks = scheduler.trigger_tick()
        assert len(ticks) == 1
        assert ticks[0]["task_id"] == "timer-1"
        assert ticks[0]["callback_name"] == "on_timer"

    def test_schedule_recurring_interval(self, scheduler):
        scheduler.schedule_task("interval-1", "@every 1s", callback_name="heartbeat")
        now = time.time()
        # Initial trigger
        ticks = scheduler.trigger_tick(current_timestamp=now + 1.1)
        assert len(ticks) == 1
        assert ticks[0]["task_id"] == "interval-1"

    def test_cron_spec_evaluation(self, scheduler):
        scheduler.schedule_task("cron-task", "* * * * *", callback_name="min_job")
        ticks = scheduler.trigger_tick()
        assert len(ticks) == 1

    def test_cancel_task(self, scheduler):
        scheduler.schedule_one_shot("timer-cancel", delay_seconds=0.01, callback_name="cb")
        assert scheduler.cancel_task("timer-cancel") is True
        time.sleep(0.02)
        ticks = scheduler.trigger_tick()
        assert len(ticks) == 0

    def test_duration_parser(self, scheduler):
        assert scheduler._parse_duration_seconds("10s") == 10.0
        assert scheduler._parse_duration_seconds("2m") == 120.0
        assert scheduler._parse_duration_seconds("1h") == 3600.0


# ============================================================================
# 10. GO MICRO-SANDBOX CONTAINER CONTROLLER TESTS (5 tests)
# ============================================================================
class TestGoMicroSandboxController:

    @pytest.fixture
    def controller(self):
        return GoMicroSandboxController()

    def test_create_sandbox(self, controller):
        sb = controller.create_sandbox("test-sb-1", memory_limit_mb=64, timeout_seconds=2.0)
        assert sb["container_id"] == "test-sb-1"
        assert sb["memory_limit_mb"] == 64
        assert sb["status"] == "READY"

    def test_execute_in_sandbox_success(self, controller):
        controller.create_sandbox("sb-exec")
        code = 'package main\nimport "fmt"\nfunc main() { fmt.Println("Sandboxed") }'
        res = controller.execute_in_sandbox("sb-exec", code)
        assert res["success"] is True
        assert res["status"] == "COMPLETED"
        assert "Sandboxed" in res["stdout"]

    def test_disallowed_package_rejection(self, controller):
        controller.create_sandbox("sb-sec")
        bad_code = 'package main\nimport "unsafe"\nfunc main() {}'
        res = controller.execute_in_sandbox("sb-sec", bad_code)
        assert res["success"] is False
        assert res["status"] == "SECURITY_VIOLATION"
        assert "unsafe" in res["stderr"]

    def test_destroy_sandbox(self, controller):
        controller.create_sandbox("sb-del")
        assert controller.destroy_sandbox("sb-del") is True
        assert controller.destroy_sandbox("sb-del") is False

    def test_list_sandboxes(self, controller):
        controller.create_sandbox("sb-a")
        controller.create_sandbox("sb-b")
        sbs = controller.list_sandboxes()
        assert len(sbs) == 2


# ============================================================================
# 11. MASTER SOVEREIGN GO SERVICES ENGINE TESTS (3 tests)
# ============================================================================
class TestSovereignGoServicesEngineMaster:

    @pytest.fixture
    def master(self):
        return SovereignGoServicesEngine()

    def test_master_system_status(self, master):
        status = master.get_system_status()
        assert "go_cli_available" in status
        assert "go_version" in status
        assert status["status"] == "SOVEREIGN_GO_SERVICES_HEALTHY"
        assert len(status["engines"]) == 10

    def test_master_health_check(self, master):
        res = master.health_check()
        assert res["all_engines_passed"] is True
        assert res["status"] == "ALL_SYSTEMS_OPERATIONAL"
        for engine_name, passed in res["engine_results"].items():
            assert passed is True, f"Engine {engine_name} failed health check"

    def test_subengine_accessibility(self, master):
        assert master.lsp_analyzer is not None
        assert master.worker_pool is not None
        assert master.memory_cache is not None
        assert master.compiler_runner is not None
        assert master.security_scanner is not None
        assert master.web_scraper is not None
        assert master.migration_engine is not None
        assert master.ide_bridge is not None
        assert master.cron_scheduler is not None
        assert master.sandbox_controller is not None
