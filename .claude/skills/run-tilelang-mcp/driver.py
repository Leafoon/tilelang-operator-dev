#!/usr/bin/env python3
"""Driver for the TileLang MCP server.

Sends JSON-RPC messages to the MCP server over stdio and prints responses.
Supports a smoke test mode that exercises all 10 tools, or individual tool calls.

Usage:
  python .claude/skills/run-tilelang-mcp/driver.py --smoke
  python .claude/skills/run-tilelang-mcp/driver.py --call inspect_tilelang_workspace
  python .claude/skills/run-tilelang-mcp/driver.py --call normalize_device_profile --args '{"vendor":"nvidia","model":"H100"}'
  python .claude/skills/run-tilelang-mcp/driver.py --call search_capabilities --args '{"query":"gemm"}'
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent  # .claude/skills/run-tilelang-mcp/ -> repo root
MCP_SERVER = REPO_ROOT / "scripts" / "tilelang_operator_mcp.py"


def send_messages(proc, messages: list[dict]) -> list[dict]:
    """Send JSON-RPC messages to the server and collect responses."""
    payload = "\n".join(json.dumps(m) for m in messages) + "\n"
    stdout, stderr = proc.communicate(input=payload, timeout=30)
    responses = []
    for line in stdout.strip().split("\n"):
        line = line.strip()
        if line:
            try:
                responses.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return responses


def make_init():
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "tilelang-driver", "version": "1.0"},
        },
    }


def make_call(tool_name: str, args: dict, msg_id: int = 2):
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": args},
    }


def make_list(msg_id: int = 2):
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "method": "tools/list",
        "params": {},
    }


def run_server(messages: list[dict]) -> list[dict]:
    """Launch the MCP server and send messages."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.Popen(
        [sys.executable, str(MCP_SERVER)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    return send_messages(proc, messages)


def pretty(result: dict) -> str:
    """Format a JSON-RPC result for display."""
    if "result" in result:
        inner = result["result"]
        if "content" in inner:
            # tools/call response
            for item in inner["content"]:
                if item.get("type") == "text":
                    try:
                        parsed = json.loads(item["text"])
                        return json.dumps(parsed, indent=2, ensure_ascii=False)
                    except json.JSONDecodeError:
                        return item["text"]
            return json.dumps(inner, indent=2)
        return json.dumps(inner, indent=2, ensure_ascii=False)
    if "error" in result:
        return json.dumps(result["error"], indent=2, ensure_ascii=False)
    return json.dumps(result, indent=2, ensure_ascii=False)


def smoke_test():
    """Run all MCP tools and report results."""
    tools = [
        ("inspect_tilelang_workspace", {}),
        ("validate_knowledge_base", {}),
        ("normalize_device_profile", {"vendor": "nvidia", "model": "H100", "target": "cuda"}),
        ("search_capabilities", {"query": "gemm"}),
        ("search_patterns", {"query": "gemm"}),
        ("search_usage_patterns", {"query": "gemm"}),
        ("lookup_apis", {"query": "gemm"}),
        ("get_source_chunks", {"query": "gemm"}),
        ("trace_semantic_graph", {"query": "gemm"}),
        ("build_operator_retrieval_plan", {"operator_intent": "basic GEMM kernel for H100"}),
        ("search_troubleshooting", {"query": "dtype mismatch"}),
        ("validate_operator_code", {"code": "@tilelang.jit\ndef gemm(A, B): return None"}),
        ("operator_development_wizard", {"current_step": 1, "operator_intent": "GEMM kernel"}),
    ]

    messages = [make_init()]
    for i, (name, args) in enumerate(tools, start=2):
        messages.append(make_call(name, args, msg_id=i))

    print(f"Running smoke test: {len(tools)} tools...\n")
    results = run_server(messages)

    expected = len(tools) + 1  # init + tool calls
    if len(results) < expected:
        print(f"ERROR: Expected {expected} responses, got {len(results)}")
        return False

    passed = 0
    failed = 0
    for i, result in enumerate(results):
        if i == 0:
            # init response
            if "result" in result and "serverInfo" in result["result"]:
                print(f"[INIT] OK - {result['result']['serverInfo']}")
            else:
                print(f"[INIT] FAIL")
            continue

        tool_name = tools[i - 1][0]
        is_error = False
        if "result" in result:
            inner = result["result"]
            if inner.get("isError"):
                is_error = True

        status = "FAIL" if is_error or "error" in result else "OK"
        if status == "OK":
            passed += 1
        else:
            failed += 1

        print(f"[{status}] {tool_name}")
        if status == "FAIL" or "--verbose" in sys.argv:
            print(textwrap.indent(pretty(result), "  "))
        print()

    print(f"Results: {passed} passed, {failed} failed out of {len(tools)} tools")
    return failed == 0


def single_call(tool_name: str, args: dict):
    """Call a single MCP tool and print the result."""
    messages = [make_init(), make_call(tool_name, args, msg_id=2)]
    results = run_server(messages)

    if len(results) >= 2:
        print(pretty(results[1]))
    else:
        print("No response from server")
        if results:
            print("Partial:", json.dumps(results, indent=2))


def list_tools():
    """List all available MCP tools."""
    messages = [make_init(), make_list(msg_id=2)]
    results = run_server(messages)

    if len(results) >= 2:
        tools = results[1].get("result", {}).get("tools", [])
        for t in tools:
            print(f"  {t['name']}")
            print(f"    {t['description']}")
            print()
    else:
        print("No response from server")


def main():
    parser = argparse.ArgumentParser(description="TileLang MCP server driver")
    parser.add_argument("--smoke", action="store_true", help="Run smoke test on all 10 tools")
    parser.add_argument("--list", action="store_true", help="List available tools")
    parser.add_argument("--call", type=str, help="Call a single tool by name")
    parser.add_argument("--args", type=str, default="{}", help="JSON arguments for --call")
    parser.add_argument("--verbose", action="store_true", help="Show full output for smoke test")
    args = parser.parse_args()

    if not MCP_SERVER.exists():
        print(f"ERROR: MCP server not found at {MCP_SERVER}", file=sys.stderr)
        sys.exit(1)

    if args.smoke:
        success = smoke_test()
        sys.exit(0 if success else 1)
    elif args.list:
        list_tools()
    elif args.call:
        try:
            tool_args = json.loads(args.args)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in --args: {e}", file=sys.stderr)
            sys.exit(1)
        single_call(args.call, tool_args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
