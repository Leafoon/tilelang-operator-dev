"""Executable tests for the TileLang MCP server.

Run with: python -m pytest tests/test_mcp_server.py -v
"""
import json
import os
import ast
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MCP_SERVER = REPO_ROOT / "scripts" / "tilelang_operator_mcp.py"


def run_mcp(*messages: dict) -> list[dict]:
    """Send JSON-RPC messages to the MCP server and return parsed responses."""
    init = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"},
        },
    }
    payload = "\n".join(json.dumps(m) for m in [init, *messages]) + "\n"
    proc = subprocess.Popen(
        [sys.executable, str(MCP_SERVER)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    stdout, _ = proc.communicate(input=payload, timeout=30)
    results = []
    for line in stdout.strip().split("\n"):
        line = line.strip()
        if line:
            results.append(json.loads(line))
    return results


def call_tool(name: str, args: dict | None = None) -> dict:
    """Call a single MCP tool and return the result payload."""
    msg = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {"name": name, "arguments": args or {}},
    }
    results = run_mcp(msg)
    assert len(results) >= 2, f"Expected 2 responses, got {len(results)}"
    return results[1]


def get_tool_result(name: str, args: dict | None = None) -> dict:
    """Call a tool and return the parsed JSON content."""
    resp = call_tool(name, args)
    assert "result" in resp, f"No result in response: {resp}"
    inner = resp["result"]
    assert not inner.get("isError"), f"Tool returned error: {inner}"
    text = inner["content"][0]["text"]
    return json.loads(text)


# --- Server initialization ---


class TestServerInit:
    def test_initialize(self):
        results = run_mcp()
        assert len(results) == 1
        init = results[0]["result"]
        assert init["serverInfo"]["name"] == "tilelang-operator-knowledge"
        assert init["protocolVersion"] == "2025-03-26"

    def test_tools_list(self):
        msg = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        results = run_mcp(msg)
        assert len(results) >= 2
        tools = results[1]["result"]["tools"]
        names = {t["name"] for t in tools}
        assert "inspect_tilelang_workspace" in names
        assert "normalize_device_profile" in names
        assert len(tools) >= 12  # At least original 10 + new tools


# --- Workspace validation ---


class TestWorkspaceValidation:
    def test_inspect_workspace(self):
        result = get_tool_result("inspect_tilelang_workspace")
        assert "status" in result
        assert "operator_workspace_path" in result
        assert "tilelang_source_path" in result
        assert "workspace_mode" in result
        assert "knowledge_source" in result

    def test_validate_knowledge_base(self):
        result = get_tool_result("validate_knowledge_base")
        assert "status" in result
        assert "knowledge_source" in result
        assert result["counts"]["troubleshooting.jsonl"] > 0


# --- Device normalization ---


class TestDeviceNormalization:
    def test_nvidia_h100(self):
        result = get_tool_result("normalize_device_profile", {"vendor": "nvidia", "model": "H100", "target": "cuda"})
        assert result["status"] == "passed"
        assert result["vendor"] == "NVIDIA"
        assert result["model"] == "H100"
        assert result["suggested_target"] == "cuda"
        assert result["confidence"] >= 0.75

    def test_nvidia_h100_auto_target(self):
        result = get_tool_result("normalize_device_profile", {"vendor": "nvidia", "model": "H100"})
        assert result["vendor"] == "NVIDIA"
        assert "sm_90" in result["suggested_target"]
        assert result["confidence"] >= 0.9

    def test_amd_mi300x(self):
        result = get_tool_result("normalize_device_profile", {"vendor": "amd", "model": "MI300X"})
        assert result["vendor"] == "AMD"
        assert result["suggested_target"] == "hip"
        assert result["confidence"] == 0.5

    def test_cpu(self):
        result = get_tool_result("normalize_device_profile", {"vendor": "cpu", "model": "Xeon"})
        assert result["vendor"] == "CPU"

    def test_unknown_device(self):
        result = get_tool_result("normalize_device_profile", {"vendor": "unknown", "model": "unknown"})
        assert result["status"] == "constrained"
        assert result["vendor"] == "unknown"

    def test_model_only_no_vendor(self):
        """Passing only model (not matching known patterns) gives low confidence."""
        result = get_tool_result("normalize_device_profile", {"model": "SomeUnknownChip"})
        assert result["confidence"] <= 0.5


# --- Knowledge base search ---


class TestSearchCapabilities:
    def test_search_gemm(self):
        result = get_tool_result("search_capabilities", {"query": "gemm"})
        assert result["status"] == "passed"
        assert len(result["results"]) > 0
        first = result["results"][0]
        assert "capability_id" in first
        assert "gemm" in first["capability_id"].lower()

    def test_search_attention(self):
        result = get_tool_result("search_capabilities", {"query": "attention"})
        assert result["status"] == "passed"
        assert len(result["results"]) > 0

    def test_search_empty_query(self):
        result = get_tool_result("search_capabilities", {"query": ""})
        assert result["status"] == "passed"
        # Empty query returns all results
        assert len(result["results"]) > 0

    def test_max_results(self):
        result = get_tool_result("search_capabilities", {"query": "gemm", "max_results": 2})
        assert len(result["results"]) <= 2


class TestSearchPatterns:
    def test_search_gemm(self):
        result = get_tool_result("search_patterns", {"query": "gemm"})
        assert result["status"] == "passed"
        assert len(result["results"]) > 0

    def test_category_filter(self):
        result = get_tool_result("search_patterns", {"query": "gemm", "category": "gemm"})
        assert result["status"] == "passed"
        for r in result["results"]:
            assert "gemm" in r.get("category", "").lower()

    def test_capability_id_filter(self):
        """capability_id filter should actually filter results."""
        result = get_tool_result("search_patterns", {"query": "gemm", "capability_id": "nonexistent_xyz"})
        assert result["status"] == "passed"
        assert len(result["results"]) == 0

    def test_capability_id_filter_uses_capability_related_patterns(self):
        """capability_id should resolve through capability_map.related_patterns."""
        result = get_tool_result("search_patterns", {
            "query": "gemm",
            "capability_id": "gemm_like_patterns",
            "max_results": 8,
        })
        assert result["status"] == "passed"
        ids = {r["pattern_id"] for r in result["results"]}
        assert "pattern.gemm.basic_tiled" in ids

    def test_official_example_coverage_patterns(self):
        cases = [
            ("sm100 tcgen05 tma", "pattern.gemm.sm100_tcgen05_tma_ws"),
            ("streamk gemm", "pattern.gemm.streamk"),
            ("fusedmoe routed expert", "pattern.gemm.fused_moe"),
            ("fp8 int4 gemm cast", "pattern.gemm.low_precision_fp8_int4"),
            ("blocksparse sparse attention", "pattern.sparse.blocksparse_gemm_attention"),
            ("deepseek nsa sparse mla", "pattern.attention.deepseek_sparse_mla_nsa_sink"),
            ("linear attention kda gdn", "pattern.attention.linear_state_space"),
            ("warp specialize barrier pipeline", "pattern.schedule.warp_specialize_and_autodd"),
        ]
        for query, expected_id in cases:
            result = get_tool_result("search_patterns", {"query": query, "max_results": 5})
            assert result["status"] == "passed"
            ids = {r["pattern_id"] for r in result["results"]}
            assert expected_id in ids


class TestSearchUsagePatterns:
    def test_search(self):
        result = get_tool_result("search_usage_patterns", {"query": "gemm"})
        assert result["status"] == "passed"


class TestLookupApis:
    def test_search(self):
        result = get_tool_result("lookup_apis", {"query": "gemm"})
        assert result["status"] == "passed"
        assert len(result["results"]) > 0
        first = result["results"][0]
        assert "qualified_name" in first

    def test_visibility_filter(self):
        result = get_tool_result("lookup_apis", {"query": "gemm", "visibility": "public"})
        assert result["status"] == "passed"

    def test_t_alias_symbol_exact_match_is_ranked_first(self):
        result = get_tool_result("lookup_apis", {
            "symbols": ["T.tcgen05_gemm"],
            "max_results": 3,
        })
        assert result["status"] == "passed"
        assert result["results"][0]["qualified_name"] == "tilelang.language.gemm_op.tcgen05_gemm"
        assert result["results"][0]["relevance_score"] > result["results"][1]["relevance_score"]

    def test_symbol_only_lookup_drops_zero_score_records(self):
        result = get_tool_result("lookup_apis", {
            "symbols": ["T.alloc_tmem"],
            "max_results": 10,
        })
        assert result["status"] == "passed"
        assert result["results"]
        assert all(r["relevance_score"] > 0 for r in result["results"])


class TestGetSourceChunks:
    def test_search(self):
        result = get_tool_result("get_source_chunks", {"query": "gemm"})
        assert result["status"] == "passed"


class TestTraceSemanticGraph:
    def test_search(self):
        result = get_tool_result("trace_semantic_graph", {"query": "gemm"})
        assert result["status"] == "passed"
        assert "nodes" in result
        assert "edges" in result


# --- End-to-end ---


class TestBuildOperatorRetrievalPlan:
    def test_basic_plan(self):
        result = get_tool_result("build_operator_retrieval_plan", {
            "operator_intent": "basic GEMM kernel for H100",
            "device_profile": {"vendor": "nvidia", "model": "H100", "target": "cuda"},
        })
        assert result["status"] in ("passed", "constrained")
        assert len(result["capability_candidates"]) > 0
        assert len(result["pattern_candidates"]) > 0
        assert result["device_profile"]["vendor"] == "NVIDIA"


# --- Error handling ---


class TestErrorHandling:
    def test_unknown_tool(self):
        resp = call_tool("nonexistent_tool")
        assert "result" in resp
        inner = resp["result"]
        assert inner.get("isError") is True
        content = json.loads(inner["content"][0]["text"])
        assert "Unknown tool" in content["error"]

    def test_no_traceback_leaked(self):
        """Error responses should not contain Python tracebacks."""
        resp = call_tool("nonexistent_tool")
        text = resp["result"]["content"][0]["text"]
        assert "Traceback" not in text
        assert "File \"" not in text


# --- New tools tests ---


class TestSearchTroubleshooting:
    def test_search_by_error(self):
        result = get_tool_result("search_troubleshooting", {"query": "dtype mismatch"})
        assert result["status"] == "passed"
        assert len(result["results"]) > 0

    def test_search_by_category(self):
        result = get_tool_result("search_troubleshooting", {"query": "", "category": "compilation"})
        assert result["status"] == "passed"

    def test_uses_workspace_local_knowledge_base(self, tmp_path):
        local_kb = tmp_path / "tilelang_knowledge"
        shutil.copytree(REPO_ROOT / "resources" / "tilelang_knowledge", local_kb)
        custom_issue = {
            "issue_id": "issue.local.override",
            "title": "Local override issue",
            "category": "compilation",
            "severity": "high",
            "description": "Workspace-local troubleshooting record.",
            "error_patterns": ["local-only-error-token"],
            "solution": "Use the workspace-local troubleshooting record.",
            "example_fix": "Local fix.",
            "related_symbols": ["T.local_override"],
            "evidence": ["workspace-local"],
        }
        (local_kb / "troubleshooting.jsonl").write_text(
            json.dumps(custom_issue) + "\n",
            encoding="utf-8",
        )

        result = get_tool_result("search_troubleshooting", {
            "workspace_path": str(tmp_path),
            "query": "local-only-error-token",
        })
        assert result["status"] == "passed"
        assert result["results"][0]["issue_id"] == "issue.local.override"


class TestValidateOperatorCode:
    def test_validate_valid_code(self):
        code = """
import tilelang
import tilelang.language as T

@tilelang.jit
def gemm(A, B):
    return None
"""
        result = get_tool_result("validate_operator_code", {"code": code})
        assert result["valid"] is True

    def test_validate_empty_code(self):
        result = get_tool_result("validate_operator_code", {"code": ""})
        assert result["valid"] is False

    def test_validate_syntax_error(self):
        code = """
import tilelang
def broken(
    syntax error here
"""
        result = get_tool_result("validate_operator_code", {"code": code})
        # May fail syntax check but should handle gracefully
        assert "status" in result

    def test_accepts_official_t_alias_and_host_side_python(self):
        code = """
import tilelang
from tilelang import language as T

@tilelang.jit
def kernel(M):
    @T.prim_func
    def main(A: T.Tensor((M,), T.float32)):
        with T.Kernel(T.ceildiv(M, 128), threads=128) as bx:
            A[bx] = T.float32(0)
    return main

def host_debug():
    print("host side only")
    for i in range(3):
        pass
"""
        result = get_tool_result("validate_operator_code", {"code": code})
        assert result["valid"] is True
        warnings = "\n".join(result["warnings"])
        assert "without importing tilelang.language as T" not in warnings
        assert "Python print() inside TileLang kernels" not in warnings
        assert "Python range() inside TileLang kernels" not in warnings


class TestOperatorTemplate:
    def test_example_operator_template_is_python_syntax_valid(self):
        template_root = REPO_ROOT / "resources" / "operator_template"
        for path in [
            template_root / "init_operator.py",
            template_root / "example_operator" / "operator.py",
            template_root / "example_operator" / "test_operator.py",
            template_root / "example_operator" / "benchmark.py",
        ]:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_template_omits_default_local_knowledge_override(self):
        template_root = REPO_ROOT / "resources" / "operator_template"
        assert not (template_root / "tilelang_knowledge").exists()

    def test_template_has_no_local_cache_artifacts(self):
        template_root = REPO_ROOT / "resources" / "operator_template"
        disallowed = {".DS_Store", "__pycache__"}
        offenders = [
            path.relative_to(template_root)
            for path in template_root.rglob("*")
            if path.name in disallowed or path.suffix == ".pyc"
        ]
        assert offenders == []

    def test_example_operator_readme_uses_package_safe_commands(self):
        readme = (REPO_ROOT / "resources" / "operator_template" / "example_operator" / "README.md").read_text(encoding="utf-8")
        assert "from operator import" not in readme
        assert "python benchmark.py" not in readme
        assert "python -m example_operator.benchmark" in readme


class TestSkillEntrypoints:
    def test_operator_skill_entrypoints_are_in_sync(self):
        root_skill = (REPO_ROOT / "SKILL.md").read_text(encoding="utf-8")
        repo_local_skill = (REPO_ROOT / ".claude" / "skills" / "tilelang-operator-dev" / "SKILL.md").read_text(encoding="utf-8")
        template_skill = (REPO_ROOT / "resources" / "operator_template" / ".claude" / "skills" / "tilelang-operator-dev" / "SKILL.md").read_text(encoding="utf-8")
        assert repo_local_skill == root_skill
        assert template_skill == root_skill


class TestKnowledgeAuditScript:
    def test_audit_reports_example_coverage_without_failing(self, tmp_path):
        source = tmp_path / "tilelang"
        knowledge = tmp_path / "tilelang_knowledge"
        (source / "examples" / "gemm").mkdir(parents=True)
        (source / "examples" / "attention").mkdir(parents=True)
        (source / "examples" / "gemm" / "example.py").write_text("print('ok')\n", encoding="utf-8")
        (source / "examples" / "quickstart.py").write_text("print('root example')\n", encoding="utf-8")
        (source / "tilelang" / "language").mkdir(parents=True)
        (source / "tilelang" / "language" / "copy_op.py").write_text("def copy():\n    pass\n", encoding="utf-8")
        knowledge.mkdir()
        (knowledge / "patterns.jsonl").write_text(json.dumps({
            "pattern_id": "pattern.test",
            "source_files": ["examples/gemm/example.py"],
            "evidence": [{"file_path": "examples/gemm/example.py", "line": 1}],
        }) + "\n", encoding="utf-8")
        with (knowledge / "patterns.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "pattern_id": "pattern.root-example",
                "source_files": ["examples/quickstart.py"],
            }) + "\n")
        (knowledge / "apis.jsonl").write_text(json.dumps({
            "qualified_name": "tilelang.language.copy_op.copy",
            "file_path": "tilelang/language/copy_op.py",
            "line_start": 1,
            "line_end": 2,
        }) + "\n", encoding="utf-8")

        proc = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "audit_tilelang_knowledge.py"),
                "--tilelang-source",
                str(source),
                "--knowledge-dir",
                str(knowledge),
                "--json",
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        result = json.loads(proc.stdout)
        assert result["status"] == "passed"
        assert result["missing_reference_count"] == 0
        assert result["line_issue_count"] == 0
        assert "gemm" in result["example_coverage"]["covered_dirs"]
        assert "quickstart.py" not in result["example_coverage"]["covered_dirs"]
        assert "attention" in result["example_coverage"]["missing_dirs"]

    def test_audit_validates_nested_evidence_line_numbers(self, tmp_path):
        source = tmp_path / "tilelang"
        knowledge = tmp_path / "tilelang_knowledge"
        (source / "examples" / "gemm").mkdir(parents=True)
        (source / "examples" / "gemm" / "example.py").write_text("print('ok')\n", encoding="utf-8")
        knowledge.mkdir()
        (knowledge / "patterns.jsonl").write_text(json.dumps({
            "pattern_id": "pattern.bad-line",
            "evidence": [{"file_path": "examples/gemm/example.py", "line": 99}],
        }) + "\n", encoding="utf-8")

        proc = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "audit_tilelang_knowledge.py"),
                "--tilelang-source",
                str(source),
                "--knowledge-dir",
                str(knowledge),
                "--json",
            ],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
        )
        result = json.loads(proc.stdout)
        assert proc.returncode == 1
        assert result["status"] == "failed"
        assert result["line_issue_count"] == 1
        assert result["line_issues"][0]["file_path"] == "examples/gemm/example.py"


class TestOperatorDevelopmentWizard:
    def test_wizard_step_1(self):
        result = get_tool_result("operator_development_wizard", {"current_step": 1})
        assert result["status"] in ("in_progress", "completed")
        assert "current_step" in result
        assert "total_steps" in result

    def test_wizard_with_intent(self):
        result = get_tool_result("operator_development_wizard", {
            "current_step": 1,
            "operator_intent": "GEMM kernel for H100"
        })
        assert "operator_intent" in result
        assert result["current_step"] == 1

    def test_wizard_step_1_with_workspace_path(self):
        """Regression: step 1 auto-validation should not call a missing function."""
        result = get_tool_result("operator_development_wizard", {
            "current_step": 1,
            "workspace_path": str(REPO_ROOT),
        })
        assert result["status"] in ("in_progress", "completed")
        assert result["current_step"] == 1
        assert result["auto_completed"]
        first = result["auto_completed"][0]
        assert first["step_id"] == 1
        assert "workspace" in first["results"]
        assert "knowledge_base" in first["results"]

    def test_wizard_step_1_preserves_tilelang_source_path(self, tmp_path):
        """Regression: wizard auto-validation should pass explicit TileLang source."""
        workspace = tmp_path / "operators"
        source = tmp_path / "tilelang-source"
        workspace.mkdir()
        (source / "tilelang" / "language").mkdir(parents=True)
        (source / "tilelang" / "__init__.py").write_text("", encoding="utf-8")
        (source / "tilelang" / "language" / "__init__.py").write_text("", encoding="utf-8")
        (source / "src" / "transform").mkdir(parents=True)
        (source / "docs").mkdir()

        result = get_tool_result("operator_development_wizard", {
            "current_step": 1,
            "workspace_path": str(workspace),
            "tilelang_source_path": str(source),
        })
        first = result["auto_completed"][0]
        workspace_result = first["results"]["workspace"]
        assert workspace_result["status"] == "passed"
        assert workspace_result["tilelang_source_path"] == str(source.resolve())


class TestSetupScript:
    def test_setup_merges_existing_mcp_config(self, tmp_path):
        home = tmp_path / "home"
        claude_dir = home / ".claude"
        claude_dir.mkdir(parents=True)
        config_path = claude_dir / ".mcp.json"
        config_path.write_text(json.dumps({
            "mcpServers": {
                "existing-server": {
                    "command": "existing",
                    "args": ["keep-me"],
                }
            },
            "otherConfig": True,
        }), encoding="utf-8")

        env = os.environ.copy()
        env["HOME"] = str(home)
        subprocess.run(
            ["bash", str(REPO_ROOT / "setup.sh")],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )

        merged = json.loads(config_path.read_text(encoding="utf-8"))
        assert merged["otherConfig"] is True
        assert "existing-server" in merged["mcpServers"]
        assert "tilelang-operator-knowledge" in merged["mcpServers"]
        assert merged["mcpServers"]["tilelang-operator-knowledge"]["args"] == [
            str(REPO_ROOT / "scripts" / "tilelang_operator_mcp.py")
        ]
        assert (home / ".claude" / "skills" / "tilelang-operator-dev" / "SKILL.md").is_file()
        assert list(claude_dir.glob(".mcp.json.bak.*"))


# --- Dual-workspace mode tests ---


class TestDualWorkspaceMode:
    """Tests for the dual-workspace mode where operators are separate from TileLang source."""

    def test_inspect_workspace_returns_new_fields(self):
        """inspect_workspace should return operator_workspace_path, tilelang_source_path, and workspace_mode."""
        result = get_tool_result("inspect_tilelang_workspace")
        # New fields should always exist
        assert "operator_workspace_path" in result
        assert "tilelang_source_path" in result
        assert "workspace_mode" in result
        # workspace_mode should be either "single" or "dual"
        assert result["workspace_mode"] in ("single", "dual")

    def test_validate_knowledge_base_returns_new_fields(self):
        """validate_knowledge_base should return new dual-workspace fields."""
        result = get_tool_result("validate_knowledge_base")
        assert "operator_workspace_path" in result
        assert "tilelang_source_path" in result
        assert "workspace_mode" in result

    def test_tool_definitions_include_tilelang_source_param(self):
        """Tool definitions should include tilelang_source_path parameter where applicable."""
        # Use the existing call_tool mechanism to list tools
        msg = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        results = run_mcp(msg)
        assert len(results) >= 2  # result 0 is initialize, result 1 is tools/list
        tools = results[1]["result"]["tools"]

        # Check that key workspace tools have the new parameter
        tools_to_check = {
            "inspect_tilelang_workspace": None,
            "validate_knowledge_base": None,
            "search_capabilities": None,
            "search_patterns": None,
            "search_usage_patterns": None,
            "lookup_apis": None,
            "get_source_chunks": None,
            "build_operator_retrieval_plan": None,
        }

        for tool in tools:
            if tool["name"] in tools_to_check:
                tools_to_check[tool["name"]] = tool
                properties = tool["inputSchema"].get("properties", {})
                # These tools should now have tilelang_source_path
                assert "tilelang_source_path" in properties, \
                    f"Tool {tool['name']} missing tilelang_source_path parameter"

        # Verify all expected tools were found
        for name, tool in tools_to_check.items():
            assert tool is not None, f"Expected tool not found: {name}"


# --- Auto-detection tests ---


class TestAutoDetection:
    """Tests for the smart auto-detection of TileLang source repository."""

    def test_auto_detect_returns_candidates(self):
        """inspect_workspace should report auto-detected candidates."""
        result = get_tool_result("inspect_tilelang_workspace")
        # When running tests from tilelang-operator-dev, there should be
        # a sibling tilelang/ or the server should report detection info
        assert "status" in result
        # If auto-detected, should have auto_detected field
        if result.get("auto_detected"):
            assert "auto_detected_path" in result or "multiple_candidates" in result

    def test_multiple_candidates_reported(self):
        """When multiple candidates exist, they should be listed."""
        result = get_tool_result("inspect_tilelang_workspace")
        if result.get("multiple_candidates"):
            assert isinstance(result["multiple_candidates"], list)
            assert len(result["multiple_candidates"]) > 1
            assert "hint" in result  # Should have a hint about choosing

    def test_hint_when_no_tilelang_found(self):
        """When no TileLang source is found, should provide helpful hint."""
        result = get_tool_result("inspect_tilelang_workspace", {
            "workspace_path": "/tmp/empty_dir_that_does_not_exist"
        })
        if result.get("status") == "failed" and not result.get("is_tilelang_repo"):
            # Should have a hint about auto-detection or manual configuration
            assert "hint" in result
