"""Executable tests for the TileLang MCP server.

Run with: python -m pytest tests/test_mcp_server.py -v
"""
import json
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
        assert "workspace_path" in result
        assert "knowledge_source" in result

    def test_validate_knowledge_base(self):
        result = get_tool_result("validate_knowledge_base")
        assert "status" in result
        assert "knowledge_source" in result


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
