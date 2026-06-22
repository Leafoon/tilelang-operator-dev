#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import traceback
from pathlib import Path
from typing import Any


SUPPORTED_PROTOCOL = "2025-03-26"
SERVER_INFO = {"name": "tilelang-operator-knowledge", "version": "0.3.0"}

REPO_REQUIRED = [
    "tilelang/__init__.py",
    "tilelang/language/__init__.py",
]
REPO_ANY_DIRS = [
    "src/transform",
    "src/op",
]
REPO_CORPUS_DIRS = [
    "examples",
    "testing",
    "docs",
]
KNOWLEDGE_REQUIRED = [
    "retrieval_plan.md",
    "capability_map.json",
    "patterns.jsonl",
    "usage_patterns.jsonl",
    "apis.jsonl",
    "source_chunks.jsonl",
    "semantic_graph.json",
    "semantic_graph.mmd",
    "manifest.json",
    "README.md",
]
JSON_FILES = ["capability_map.json", "semantic_graph.json", "manifest.json"]
JSONL_FILES = ["patterns.jsonl", "usage_patterns.jsonl", "apis.jsonl", "source_chunks.jsonl"]


class McpError(Exception):
    pass


def send(message: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(message, ensure_ascii=False, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def respond(msg_id: Any, result: dict[str, Any]) -> None:
    if msg_id is not None:
        send({"jsonrpc": "2.0", "id": msg_id, "result": result})


def error(msg_id: Any, code: int, message: str) -> None:
    if msg_id is not None:
        send({"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}})


def workspace_root(value: str | None) -> Path:
    return Path(value or ".").expanduser().resolve()


def knowledge_dir(root: Path) -> Path:
    return root / "tilelang_knowledge"


def file_exists(root: Path, rel: str) -> bool:
    return (root / rel).exists()


def inspect_workspace(args: dict[str, Any]) -> dict[str, Any]:
    root = workspace_root(args.get("workspace_path"))
    missing_repo = [p for p in REPO_REQUIRED if not file_exists(root, p)]
    has_backend = any((root / p).is_dir() for p in REPO_ANY_DIRS)
    has_corpus = any((root / p).is_dir() for p in REPO_CORPUS_DIRS)
    if not has_backend:
        missing_repo.append("one of: " + ", ".join(REPO_ANY_DIRS))
    if not has_corpus:
        missing_repo.append("one of: " + ", ".join(REPO_CORPUS_DIRS))

    kdir = knowledge_dir(root)
    missing_knowledge = []
    if not kdir.is_dir():
        missing_knowledge.append("tilelang_knowledge/")
    else:
        missing_knowledge = [f"tilelang_knowledge/{p}" for p in KNOWLEDGE_REQUIRED if not (kdir / p).is_file()]

    status = "passed" if not missing_repo and not missing_knowledge else "failed"
    return {
        "status": status,
        "workspace_path": str(root),
        "repo_root": str(root) if not missing_repo else None,
        "knowledge_path": str(kdir) if kdir.is_dir() else None,
        "is_tilelang_repo": not missing_repo,
        "has_knowledge_base": kdir.is_dir() and not missing_knowledge,
        "missing_repo_indicators": missing_repo,
        "missing_knowledge_files": missing_knowledge,
    }


def parse_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, str(exc)


def parse_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    try:
        for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    records.append(obj)
                else:
                    errors.append(f"line {idx}: expected object")
            except Exception as exc:
                errors.append(f"line {idx}: {exc}")
    except Exception as exc:
        errors.append(str(exc))
    return records, errors


def validate_knowledge(args: dict[str, Any]) -> dict[str, Any]:
    root = workspace_root(args.get("workspace_path"))
    kdir = knowledge_dir(root)
    missing = [p for p in KNOWLEDGE_REQUIRED if not (kdir / p).is_file()]
    parse_errors: dict[str, Any] = {}
    counts: dict[str, int] = {}
    manifest_summary: dict[str, Any] = {}

    if kdir.is_dir():
        for name in JSON_FILES:
            path = kdir / name
            if path.is_file():
                obj, err = parse_json(path)
                if err:
                    parse_errors[name] = err
                elif name == "manifest.json" and isinstance(obj, dict):
                    manifest_summary = {
                        "repo_name": obj.get("repo_name"),
                        "analyzed_at": obj.get("analyzed_at"),
                        "source_roots": obj.get("source_roots"),
                        "total_python_files": obj.get("total_python_files"),
                        "device_integration": obj.get("device_integration"),
                    }
            elif name not in missing:
                missing.append(name)
        for name in JSONL_FILES:
            path = kdir / name
            if path.is_file():
                records, errors = parse_jsonl(path)
                counts[name] = len(records)
                if errors:
                    parse_errors[name] = errors[:10]
            elif name not in missing:
                missing.append(name)

    status = "passed" if not missing and not parse_errors else "failed"
    return {
        "status": status,
        "workspace_path": str(root),
        "knowledge_path": str(kdir) if kdir.is_dir() else None,
        "missing_files": [f"tilelang_knowledge/{p}" for p in missing],
        "parse_errors": parse_errors,
        "counts": counts,
        "manifest": manifest_summary,
    }


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        return " ".join(normalize_text(v) for v in value)
    if isinstance(value, dict):
        return " ".join(f"{k} {normalize_text(v)}" for k, v in value.items())
    return str(value)


def tokens(query: str) -> list[str]:
    return [t for t in re.split(r"[^A-Za-z0-9_+.-]+", query.lower()) if len(t) >= 2]


def score_record(record: dict[str, Any], query: str, fields: list[str]) -> float:
    query_terms = tokens(query)
    if not query_terms:
        return 0.0
    hay = " ".join(normalize_text(record.get(f)) for f in fields).lower()
    score = 0.0
    for term in query_terms:
        if term in hay:
            score += 1.0
        if re.search(rf"\b{re.escape(term)}\b", hay):
            score += 0.5
    return score


def capability_keyword_boost(capability_id: str, query: str) -> float:
    q = query.lower()
    boosts = {
        "gemm_like_patterns": ["gemm", "matmul", "matrix multiply", "grouped", "split-k", "dequant", "sparse"],
        "attention_like_patterns": ["attention", "flash", "decode", "mha", "gqa", "mla", "softmax"],
        "reductions": ["reduction", "reduce", "sum", "max", "norm", "rmsnorm", "softmax", "topk"],
        "convolution_like_patterns": ["conv", "convolution", "im2col"],
        "elementwise_and_fusion_patterns": ["elementwise", "fusion", "epilogue", "activation", "cast"],
        "tensor_intrinsics": ["wgmma", "tcgen", "tensorcore", "tensor core", "mma", "mfma", "gemm"],
        "memory_movement": ["copy", "tma", "async", "cp.async", "shared", "global", "memory"],
        "pipelining": ["pipeline", "pipelined", "num_stages", "async"],
        "tiling_and_schedule": ["tile", "schedule", "layout", "thread", "block", "swizzle"],
        "testing_and_validation_support": ["validate", "test", "benchmark", "profile", "profiler"],
    }
    weight = 5.0 if capability_id == "gemm_like_patterns" and any(t in q for t in ["gemm", "matmul"]) else 3.0
    return sum(weight for term in boosts.get(capability_id, []) if term in q)


def load_json(root: Path, name: str) -> dict[str, Any]:
    path = knowledge_dir(root) / name
    if not path.is_file():
        raise McpError(f"Missing tilelang_knowledge/{name}")
    obj, err = parse_json(path)
    if err:
        raise McpError(f"Cannot parse {name}: {err}")
    if not isinstance(obj, dict):
        raise McpError(f"{name} must contain a JSON object")
    return obj


def load_jsonl(root: Path, name: str) -> list[dict[str, Any]]:
    path = knowledge_dir(root) / name
    if not path.is_file():
        raise McpError(f"Missing tilelang_knowledge/{name}")
    records, errors = parse_jsonl(path)
    if errors:
        raise McpError(f"Cannot parse {name}: {errors[0]}")
    return records


def limit_results(records: list[dict[str, Any]], max_results: Any) -> list[dict[str, Any]]:
    try:
        limit = int(max_results or 8)
    except Exception:
        limit = 8
    return records[: max(1, min(limit, 50))]


def normalize_device(args: dict[str, Any]) -> dict[str, Any]:
    vendor_in = normalize_text(args.get("vendor")).lower()
    model = normalize_text(args.get("model")).strip()
    target = normalize_text(args.get("target") or args.get("arch")).strip()
    combined = f"{vendor_in} {model} {target}".lower()
    vendor = "unknown"
    suggested = target or None
    confidence = 0.4
    notes: list[str] = []

    if "nvidia" in combined or "cuda" in combined or re.search(r"\b(a100|h100|b100|rtx|sm_)", combined):
        vendor = "NVIDIA"
        if not suggested:
            if "a100" in combined:
                suggested, confidence = "cuda -arch=sm_80", 0.9
            elif "h100" in combined or "hopper" in combined:
                suggested, confidence = "cuda -arch=sm_90", 0.9
            elif "b100" in combined or "blackwell" in combined:
                suggested, confidence = "cuda -arch=sm_100a", 0.75
                notes.append("Blackwell target support should be checked against the current TileLang repository.")
            elif "sm_" in combined:
                suggested, confidence = f"cuda -arch={re.search(r'sm_[0-9a-z]+', combined).group(0)}", 0.85
            else:
                suggested, confidence = "cuda", 0.55
                notes.append("Exact NVIDIA compute capability was not provided.")
    elif "amd" in combined or "hip" in combined or "rocm" in combined or "mi300" in combined or "mi350" in combined or "gfx" in combined:
        vendor = "AMD"
        match = re.search(r"gfx[0-9a-z]+", combined)
        if suggested:
            confidence = 0.75
        elif match:
            suggested, confidence = f"hip -mcpu={match.group(0)}", 0.85
        else:
            suggested, confidence = "hip", 0.5
            notes.append("Exact AMD gfx architecture is unknown; do not invent gfxXXX.")
    elif "cpu" in combined or "llvm" in combined or target == "c":
        vendor, suggested, confidence = "CPU", suggested or "llvm", 0.8
    elif "apple" in combined or "m1" in combined or "m2" in combined or "m3" in combined or "metal" in combined:
        vendor, suggested, confidence = "Apple", suggested or "metal", 0.65
    elif "webgpu" in combined:
        vendor, suggested, confidence = "WebGPU", suggested or "webgpu", 0.65
    else:
        notes.append("Device vendor/model could not be mapped to a known TileLang target family.")

    if target:
        notes.append("User supplied an explicit target/arch; preserve it unless repository evidence contradicts it.")
        confidence = max(confidence, 0.75)

    return {
        "status": "passed" if vendor != "unknown" else "constrained",
        "vendor": vendor,
        "model": model or None,
        "suggested_target": suggested,
        "confidence": round(confidence, 2),
        "uncertainty_notes": notes,
    }


def search_capabilities(args: dict[str, Any]) -> dict[str, Any]:
    root = workspace_root(args.get("workspace_path"))
    query = normalize_text(args.get("query"))
    cap_doc = load_json(root, "capability_map.json")
    records = cap_doc.get("capabilities", [])
    if not isinstance(records, list):
        records = []
    scored = []
    for rec in records:
        if not isinstance(rec, dict):
            continue
        cap_id = normalize_text(rec.get("capability_id"))
        score = score_record(rec, query, ["capability_id", "summary", "primary_symbols", "related_patterns", "when_to_use", "device_adaptation"])
        score += capability_keyword_boost(cap_id, query)
        if score > 0 or not query:
            scored.append((score, rec))
    scored.sort(key=lambda x: (x[0], x[1].get("confidence", 0)), reverse=True)
    results = []
    for rec in limit_results([r for _, r in scored], args.get("max_results")):
        results.append({
            "capability_id": rec.get("capability_id"),
            "summary": rec.get("summary"),
            "primary_symbols": rec.get("primary_symbols"),
            "related_patterns": rec.get("related_patterns"),
            "device_adaptation": rec.get("device_adaptation"),
            "confidence": rec.get("confidence"),
            "evidence": rec.get("evidence"),
        })
    return {"status": "passed", "results": results}


def search_patterns(args: dict[str, Any]) -> dict[str, Any]:
    root = workspace_root(args.get("workspace_path"))
    query = normalize_text(args.get("query"))
    category = normalize_text(args.get("category")).lower()
    task_family = normalize_text(args.get("task_family")).lower()
    capability_id = normalize_text(args.get("capability_id"))
    records = load_jsonl(root, "patterns.jsonl")
    scored = []
    for rec in records:
        if category and category not in normalize_text(rec.get("category")).lower():
            continue
        if task_family and task_family not in normalize_text(rec.get("task_family")).lower():
            continue
        hay = normalize_text(rec)
        if capability_id and capability_id not in hay:
            pass
        score = score_record(rec, query + " " + capability_id, ["pattern_id", "pattern_name", "category", "task_family", "summary", "required_symbols", "related_usage_patterns", "device_strategy"])
        if score > 0 or not query:
            scored.append((score, rec))
    scored.sort(key=lambda x: (x[0], x[1].get("confidence", 0)), reverse=True)
    results = []
    for rec in limit_results([r for _, r in scored], args.get("max_results")):
        results.append({
            "pattern_id": rec.get("pattern_id"),
            "pattern_name": rec.get("pattern_name"),
            "category": rec.get("category"),
            "task_family": rec.get("task_family"),
            "required_symbols": rec.get("required_symbols"),
            "control_flow_shape": rec.get("control_flow_shape"),
            "memory_flow_shape": rec.get("memory_flow_shape"),
            "device_strategy": rec.get("device_strategy"),
            "reuse_guidance": rec.get("reuse_guidance"),
            "confidence": rec.get("confidence"),
            "evidence": rec.get("evidence"),
        })
    return {"status": "passed", "results": results}


def search_usage_patterns(args: dict[str, Any]) -> dict[str, Any]:
    root = workspace_root(args.get("workspace_path"))
    query = normalize_text(args.get("query"))
    pattern_id = normalize_text(args.get("pattern_id"))
    symbols = normalize_text(args.get("symbols"))
    records = load_jsonl(root, "usage_patterns.jsonl")
    scored = []
    for rec in records:
        score = score_record(rec, query + " " + pattern_id + " " + symbols, ["usage_id", "scenario", "goal", "ordered_steps", "symbols_used", "source_files", "device_execution_notes"])
        if score > 0 or not query:
            scored.append((score, rec))
    scored.sort(key=lambda x: (x[0], x[1].get("confidence", 0)), reverse=True)
    results = []
    for rec in limit_results([r for _, r in scored], args.get("max_results")):
        results.append({
            "usage_id": rec.get("usage_id"),
            "scenario": rec.get("scenario"),
            "goal": rec.get("goal"),
            "ordered_steps": rec.get("ordered_steps"),
            "symbols_used": rec.get("symbols_used"),
            "prerequisites": rec.get("prerequisites"),
            "failure_modes": rec.get("failure_modes"),
            "device_execution_notes": rec.get("device_execution_notes"),
            "confidence": rec.get("confidence"),
            "evidence": rec.get("evidence"),
        })
    return {"status": "passed", "results": results}


def lookup_apis(args: dict[str, Any]) -> dict[str, Any]:
    root = workspace_root(args.get("workspace_path"))
    query = normalize_text(args.get("query"))
    symbols = normalize_text(args.get("symbols"))
    visibility = normalize_text(args.get("visibility")).lower()
    module = normalize_text(args.get("module")).lower()
    records = load_jsonl(root, "apis.jsonl")
    scored = []
    for rec in records:
        if visibility and visibility != normalize_text(rec.get("visibility")).lower():
            continue
        if module and module not in normalize_text(rec.get("module")).lower():
            continue
        score = score_record(rec, query + " " + symbols, ["qualified_name", "signature", "docstring", "short_summary", "operator_relevance", "module"])
        if score > 0 or not query:
            scored.append((score, rec))
    scored.sort(key=lambda x: (x[0], normalize_text(x[1].get("visibility")) == "public"), reverse=True)
    results = []
    for rec in limit_results([r for _, r in scored], args.get("max_results")):
        results.append({
            "qualified_name": rec.get("qualified_name"),
            "symbol_type": rec.get("symbol_type"),
            "signature": rec.get("signature"),
            "visibility": rec.get("visibility"),
            "module": rec.get("module"),
            "file_path": rec.get("file_path"),
            "line_start": rec.get("line_start"),
            "line_end": rec.get("line_end"),
            "operator_relevance": rec.get("operator_relevance"),
            "evidence": rec.get("evidence"),
        })
    return {"status": "passed", "results": results}


def get_source_chunks(args: dict[str, Any]) -> dict[str, Any]:
    root = workspace_root(args.get("workspace_path"))
    query = normalize_text(args.get("query"))
    capability_id = normalize_text(args.get("capability_id"))
    pattern_id = normalize_text(args.get("pattern_id"))
    symbols = normalize_text(args.get("symbols"))
    records = load_jsonl(root, "source_chunks.jsonl")
    scored = []
    for rec in records:
        score = score_record(rec, query + " " + capability_id + " " + pattern_id + " " + symbols, ["chunk_id", "symbols", "summary", "why_it_matters", "related_capabilities", "related_patterns", "device_notes"])
        if capability_id and capability_id in normalize_text(rec.get("related_capabilities")):
            score += 2
        if pattern_id and pattern_id in normalize_text(rec.get("related_patterns")):
            score += 2
        if score > 0 or not query:
            scored.append((score, rec))
    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for rec in limit_results([r for _, r in scored], args.get("max_results")):
        source = normalize_text(rec.get("source"))
        if len(source) > 4000:
            source = source[:4000] + "\n...[truncated]..."
        results.append({
            "chunk_id": rec.get("chunk_id"),
            "file_path": rec.get("file_path"),
            "start_line": rec.get("start_line"),
            "end_line": rec.get("end_line"),
            "summary": rec.get("summary"),
            "why_it_matters": rec.get("why_it_matters"),
            "symbols": rec.get("symbols"),
            "device_notes": rec.get("device_notes"),
            "related_capabilities": rec.get("related_capabilities"),
            "related_patterns": rec.get("related_patterns"),
            "source_excerpt": source,
        })
    return {"status": "passed", "results": results}


def trace_semantic_graph(args: dict[str, Any]) -> dict[str, Any]:
    root = workspace_root(args.get("workspace_path"))
    graph = load_json(root, "semantic_graph.json")
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    node_id = normalize_text(args.get("node_id"))
    query = normalize_text(args.get("query"))
    edge_type = normalize_text(args.get("edge_type"))
    max_results = args.get("max_results")

    matched_nodes = []
    for n in nodes if isinstance(nodes, list) else []:
        if not isinstance(n, dict):
            continue
        if node_id and n.get("id") == node_id:
            matched_nodes.append(n)
        elif query and score_record(n, query, ["id", "label", "type", "attrs"]) > 0:
            matched_nodes.append(n)
    node_ids = {n.get("id") for n in matched_nodes}
    matched_edges = []
    for e in edges if isinstance(edges, list) else []:
        if not isinstance(e, dict):
            continue
        if edge_type and e.get("edge_type") != edge_type:
            continue
        if node_id and (e.get("source") == node_id or e.get("target") == node_id):
            matched_edges.append(e)
        elif node_ids and (e.get("source") in node_ids or e.get("target") in node_ids):
            matched_edges.append(e)
        elif query and score_record(e, query, ["source", "target", "edge_type"]) > 0:
            matched_edges.append(e)
    return {
        "status": "passed",
        "nodes": limit_results(matched_nodes, max_results),
        "edges": limit_results(matched_edges, max_results),
    }


def build_operator_retrieval_plan(args: dict[str, Any]) -> dict[str, Any]:
    root = workspace_root(args.get("workspace_path"))
    intent = normalize_text(args.get("operator_intent"))
    device = args.get("device_profile") or {}
    device_result = normalize_device(device if isinstance(device, dict) else {"model": normalize_text(device)})
    caps = search_capabilities({"workspace_path": str(root), "query": intent, "max_results": 3})["results"]
    cap_id = caps[0]["capability_id"] if caps else ""
    patterns = search_patterns({"workspace_path": str(root), "query": intent, "capability_id": cap_id, "max_results": 3})["results"]
    pat_id = patterns[0]["pattern_id"] if patterns else ""
    usages = search_usage_patterns({"workspace_path": str(root), "query": intent, "pattern_id": pat_id, "max_results": 3})["results"]
    symbols = []
    if patterns:
        symbols = patterns[0].get("required_symbols") or []
    apis = lookup_apis({"workspace_path": str(root), "query": intent, "symbols": symbols, "max_results": 8})["results"]
    chunks = get_source_chunks({"workspace_path": str(root), "query": intent, "capability_id": cap_id, "pattern_id": pat_id, "symbols": symbols, "max_results": 3})["results"]
    unresolved = []
    if not caps:
        unresolved.append("No capability candidate found.")
    if not patterns:
        unresolved.append("No pattern candidate found.")
    if device_result["status"] == "constrained":
        unresolved.extend(device_result.get("uncertainty_notes", []))
    return {
        "status": "passed" if caps and patterns else "constrained",
        "operator_intent": intent,
        "device_profile": device_result,
        "capability_candidates": caps,
        "pattern_candidates": patterns,
        "usage_candidates": usages,
        "api_candidates": apis,
        "source_fallback_candidates": chunks,
        "confidence": min([x.get("confidence", 0.5) or 0.5 for x in caps[:1] + patterns[:1]] or [0.4]),
        "unresolved_questions": unresolved,
    }


TOOLS = {
    "inspect_tilelang_workspace": inspect_workspace,
    "validate_knowledge_base": validate_knowledge,
    "normalize_device_profile": normalize_device,
    "search_capabilities": search_capabilities,
    "search_patterns": search_patterns,
    "search_usage_patterns": search_usage_patterns,
    "lookup_apis": lookup_apis,
    "get_source_chunks": get_source_chunks,
    "trace_semantic_graph": trace_semantic_graph,
    "build_operator_retrieval_plan": build_operator_retrieval_plan,
}


def tool_definitions() -> list[dict[str, Any]]:
    base_props = {"workspace_path": {"type": "string", "description": "TileLang repository workspace root."}}
    return [
        {"name": "inspect_tilelang_workspace", "description": "Validate TileLang repository and tilelang_knowledge presence.", "inputSchema": {"type": "object", "properties": base_props}},
        {"name": "validate_knowledge_base", "description": "Validate required delivery files and parse JSON/JSONL.", "inputSchema": {"type": "object", "properties": base_props}},
        {"name": "normalize_device_profile", "description": "Normalize vendor/model/target for device-aware TileLang operator planning.", "inputSchema": {"type": "object", "properties": {"vendor": {"type": "string"}, "model": {"type": "string"}, "target": {"type": "string"}, "arch": {"type": "string"}}}},
        {"name": "search_capabilities", "description": "Search capability_map.json.", "inputSchema": {"type": "object", "properties": {**base_props, "query": {"type": "string"}, "max_results": {"type": "integer"}}}},
        {"name": "search_patterns", "description": "Search patterns.jsonl.", "inputSchema": {"type": "object", "properties": {**base_props, "query": {"type": "string"}, "category": {"type": "string"}, "task_family": {"type": "string"}, "capability_id": {"type": "string"}, "max_results": {"type": "integer"}}}},
        {"name": "search_usage_patterns", "description": "Search usage_patterns.jsonl.", "inputSchema": {"type": "object", "properties": {**base_props, "query": {"type": "string"}, "pattern_id": {"type": "string"}, "symbols": {"type": "array", "items": {"type": "string"}}, "max_results": {"type": "integer"}}}},
        {"name": "lookup_apis", "description": "Search apis.jsonl for symbols and signatures.", "inputSchema": {"type": "object", "properties": {**base_props, "query": {"type": "string"}, "symbols": {"type": "array", "items": {"type": "string"}}, "visibility": {"type": "string"}, "module": {"type": "string"}, "max_results": {"type": "integer"}}}},
        {"name": "get_source_chunks", "description": "Retrieve source fallback chunks.", "inputSchema": {"type": "object", "properties": {**base_props, "query": {"type": "string"}, "capability_id": {"type": "string"}, "pattern_id": {"type": "string"}, "symbols": {"type": "array", "items": {"type": "string"}}, "max_results": {"type": "integer"}}}},
        {"name": "trace_semantic_graph", "description": "Trace semantic graph nodes and edges.", "inputSchema": {"type": "object", "properties": {**base_props, "node_id": {"type": "string"}, "query": {"type": "string"}, "edge_type": {"type": "string"}, "max_results": {"type": "integer"}}}},
        {"name": "build_operator_retrieval_plan", "description": "Build a structured retrieval plan for an operator intent.", "inputSchema": {"type": "object", "properties": {**base_props, "operator_intent": {"type": "string"}, "device_profile": {"type": "object"}}}},
    ]


def handle(msg: dict[str, Any]) -> None:
    method = msg.get("method")
    msg_id = msg.get("id")
    params = msg.get("params") or {}
    if method == "initialize":
        respond(msg_id, {"protocolVersion": SUPPORTED_PROTOCOL, "capabilities": {"tools": {"listChanged": False}}, "serverInfo": SERVER_INFO})
    elif method == "notifications/initialized":
        return
    elif method == "ping":
        respond(msg_id, {})
    elif method == "tools/list":
        respond(msg_id, {"tools": tool_definitions()})
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        if name not in TOOLS:
            raise McpError(f"Unknown tool: {name}")
        result = TOOLS[name](args)
        respond(msg_id, {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}], "isError": False})
    else:
        error(msg_id, -32601, f"Method not found: {method}")


def run_server() -> None:
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            payload = json.loads(raw)
            if isinstance(payload, list):
                for item in payload:
                    handle(item)
            else:
                handle(payload)
        except Exception as exc:
            err = {"error": str(exc), "traceback": traceback.format_exc(limit=3)}
            msg_id = None
            try:
                msg_id = payload.get("id") if isinstance(payload, dict) else None  # type: ignore[name-defined]
            except Exception:
                pass
            respond(msg_id, {"content": [{"type": "text", "text": json.dumps(err, ensure_ascii=False, indent=2)}], "isError": True})


def main() -> None:
    parser = argparse.ArgumentParser(description="TileLang operator knowledge MCP server.")
    parser.add_argument("--check", action="store_true", help="Run a syntax/import self-check and exit.")
    args = parser.parse_args()
    if args.check:
        print(json.dumps({"status": "passed", "serverInfo": SERVER_INFO}, ensure_ascii=False))
        return
    run_server()


if __name__ == "__main__":
    main()
