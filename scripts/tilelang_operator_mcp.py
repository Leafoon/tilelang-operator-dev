#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# Force UTF-8 on Windows where stdout defaults to GBK/CP936
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

# Load environment variables from .env file (if python-dotenv is available)
# This enables dual-workspace mode even when MCP doesn't pass env vars
try:
    from dotenv import load_dotenv
    cwd = Path.cwd()
    env_file = cwd / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass


SUPPORTED_PROTOCOL = "2025-03-26"
SERVER_INFO = {"name": "tilelang-operator-knowledge", "version": "0.4.3"}

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
    "troubleshooting.jsonl",
]
JSON_FILES = ["capability_map.json", "semantic_graph.json", "manifest.json"]
JSONL_FILES = ["patterns.jsonl", "usage_patterns.jsonl", "apis.jsonl", "source_chunks.jsonl", "troubleshooting.jsonl"]


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


def _is_valid_tilelang_repo(path: Path) -> bool:
    """Check if a path looks like a valid TileLang source repository."""
    return all((path / p).exists() for p in REPO_REQUIRED)


def _auto_detect_tilelang(workspace: Path) -> list[Path]:
    """Auto-detect TileLang source repository by checking sibling and parent directories.

    Search scope (bounded):
    - Sibling: {workspace}/../tilelang/
    - Sibling: {skill_root}/../../tilelang/
    - Up to 3 parent levels: {workspace}/../../tilelang/, etc.

    Returns list of valid candidates (may be empty).
    """
    candidates = []

    # Sibling of workspace
    sibling = workspace.parent / "tilelang"
    if sibling not in candidates and _is_valid_tilelang_repo(sibling):
        candidates.append(sibling)

    # Sibling of skill repo (two levels up from script)
    skill_sibling = SKILL_ROOT.parent / "tilelang"
    if skill_sibling not in candidates and _is_valid_tilelang_repo(skill_sibling):
        candidates.append(skill_sibling)

    # Walk up to 3 parent levels
    current = workspace.resolve()
    for _ in range(3):
        parent_candidate = current / "tilelang"
        if parent_candidate not in candidates and _is_valid_tilelang_repo(parent_candidate):
            candidates.append(parent_candidate)
        parent = current.parent
        if parent == current:  # reached filesystem root
            break
        current = parent

    return candidates


def tilelang_source_root(workspace: Path, tilelang_path: str | None) -> Path:
    """Resolve TileLang source repository path.

    Priority (highest to lowest):
    1. Explicit tool parameter: tilelang_source_path
    2. Environment variable: TILELANG_SOURCE_PATH
    3. Auto-detect: sibling tilelang/ directory (zero config)
    4. Auto-detect: walk up to 3 parent levels looking for tilelang/
    5. Fallback: workspace_path (backward compatibility)

    Supports dual-workspace mode: operator workspace + TileLang source.
    """
    # 1. Try explicit parameter first
    if tilelang_path:
        return Path(tilelang_path).expanduser().resolve()

    # 2. Try environment variable
    env_path = os.environ.get("TILELANG_SOURCE_PATH")
    if env_path:
        return Path(env_path).expanduser().resolve()

    # 3-4. Auto-detect (smart discovery)
    candidates = _auto_detect_tilelang(workspace)
    if candidates:
        # Return the first found; if multiple, the caller can use hint to ask user
        return candidates[0]

    # 5. Fallback to workspace (backward compatibility)
    return workspace


def tilelang_source_candidates(workspace: Path) -> list[Path]:
    """Return all auto-detected TileLang source candidates.

    Used when multiple candidates are found and user needs to choose.
    """
    return _auto_detect_tilelang(workspace)


# Built-in knowledge base bundled with the skill package
SKILL_ROOT = Path(__file__).resolve().parent.parent
BUILTIN_KNOWLEDGE = SKILL_ROOT / "resources" / "tilelang_knowledge"


def knowledge_dir(root: Path) -> Path:
    """Resolve tilelang_knowledge directory.

    Priority:
    1. Workspace-local tilelang_knowledge/ (user copied or generated) — only if it has required files
    2. Skill-bundled resources/tilelang_knowledge/ (built-in fallback)
    """
    local = root / "tilelang_knowledge"
    if local.is_dir():
        # Only use a local delivery set when it is complete enough to avoid
        # silently mixing workspace records with bundled records.
        local_has_files = all((local / f).is_file() for f in KNOWLEDGE_REQUIRED)
        if local_has_files:
            return local
    if BUILTIN_KNOWLEDGE.is_dir():
        return BUILTIN_KNOWLEDGE
    return local  # return the expected path for error messages


def file_exists(root: Path, rel: str) -> bool:
    return (root / rel).exists()


def inspect_workspace(args: dict[str, Any]) -> dict[str, Any]:
    # Operator workspace (where your operators live)
    operator_workspace = workspace_root(args.get("workspace_path"))

    # TileLang source path (may be different from operator workspace)
    tilelang_source = tilelang_source_root(operator_workspace, args.get("tilelang_source_path"))

    # Auto-detect candidates for reporting
    candidates = tilelang_source_candidates(operator_workspace)

    # Validate TileLang source repository
    missing_repo = [p for p in REPO_REQUIRED if not file_exists(tilelang_source, p)]
    has_backend = any((tilelang_source / p).is_dir() for p in REPO_ANY_DIRS)
    has_corpus = any((tilelang_source / p).is_dir() for p in REPO_CORPUS_DIRS)
    if not has_backend:
        missing_repo.append("one of: " + ", ".join(REPO_ANY_DIRS))
    if not has_corpus:
        missing_repo.append("one of: " + ", ".join(REPO_CORPUS_DIRS))

    # Knowledge base: look first in operator workspace, then builtin
    local_kdir = operator_workspace / "tilelang_knowledge"
    kdir = knowledge_dir(operator_workspace)
    using_builtin = kdir == BUILTIN_KNOWLEDGE
    missing_knowledge = []
    if not kdir.is_dir():
        missing_knowledge.append("tilelang_knowledge/")
    else:
        missing_knowledge = [f"tilelang_knowledge/{p}" for p in KNOWLEDGE_REQUIRED if not (kdir / p).is_file()]

    # Detect if we're in dual-workspace mode
    is_dual_workspace = str(operator_workspace) != str(tilelang_source)

    # Check if TileLang was auto-detected (not explicitly configured)
    explicit_path = args.get("tilelang_source_path") or os.environ.get("TILELANG_SOURCE_PATH")

    status = "passed" if not missing_repo and not missing_knowledge else "failed"
    result = {
        "status": status,
        "operator_workspace_path": str(operator_workspace),
        "tilelang_source_path": str(tilelang_source),
        "workspace_mode": "dual" if is_dual_workspace else "single",
        "repo_root": str(tilelang_source) if not missing_repo else None,
        "knowledge_path": str(kdir) if kdir.is_dir() else None,
        "knowledge_source": "builtin" if using_builtin else "workspace",
        "is_tilelang_repo": not missing_repo,
        "has_knowledge_base": kdir.is_dir() and not missing_knowledge,
        "missing_repo_indicators": missing_repo,
        "missing_knowledge_files": missing_knowledge,
    }

    # Report auto-detection info
    if not explicit_path and candidates:
        if len(candidates) == 1:
            result["auto_detected"] = True
            result["auto_detected_path"] = str(candidates[0])
        else:
            result["auto_detected"] = True
            result["multiple_candidates"] = [str(c) for c in candidates]
            result["hint"] = f"Found {len(candidates)} TileLang source candidates. Use tilelang_source_path parameter to specify which one to use."

    # Add helpful hint if TileLang source not found
    if missing_repo:
        if not candidates and not explicit_path:
            result["hint"] = "TileLang source not found. Searched: sibling tilelang/, up to 3 parent levels. Use TILELANG_SOURCE_PATH env or tilelang_source_path parameter to specify manually."

    return result


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
    operator_workspace = workspace_root(args.get("workspace_path"))
    tilelang_source = tilelang_source_root(operator_workspace, args.get("tilelang_source_path"))
    is_dual_workspace = str(operator_workspace) != str(tilelang_source)

    local_kdir = operator_workspace / "tilelang_knowledge"
    kdir = knowledge_dir(operator_workspace)
    using_builtin = kdir == BUILTIN_KNOWLEDGE
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
        "operator_workspace_path": str(operator_workspace),
        "tilelang_source_path": str(tilelang_source),
        "workspace_mode": "dual" if is_dual_workspace else "single",
        "knowledge_path": str(kdir) if kdir.is_dir() else None,
        "knowledge_source": "builtin" if using_builtin else "workspace",
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


def api_symbol_aliases(value: Any) -> list[str]:
    """Return searchable aliases for API symbols such as T.copy or tl.copy."""
    raw = normalize_text(value)
    aliases: list[str] = []
    for item in re.split(r"[\s,;]+", raw):
        symbol = item.strip().strip("`'\"")
        if not symbol:
            continue
        candidates = [symbol]
        for prefix in ("T.", "tl."):
            if symbol.startswith(prefix):
                candidates.append(symbol[len(prefix):])
        if symbol.startswith("tilelang.language."):
            candidates.append(symbol.rsplit(".", 1)[-1])
        if "." in symbol:
            candidates.append(symbol.rsplit(".", 1)[-1])
        for candidate in candidates:
            lowered = candidate.lower()
            if lowered and lowered not in aliases:
                aliases.append(lowered)
    return aliases


def api_exact_symbol_boost(record: dict[str, Any], aliases: list[str]) -> tuple[float, list[str]]:
    """Boost API records whose qualified name matches requested symbol aliases."""
    if not aliases:
        return 0.0, []

    qualified = normalize_text(record.get("qualified_name")).lower()
    signature = normalize_text(record.get("signature")).lower()
    short_name = qualified.rsplit(".", 1)[-1] if qualified else ""
    signature_name = signature.split("(", 1)[0].rsplit(".", 1)[-1]

    score = 0.0
    matches: list[str] = []
    for alias in aliases:
        tail = alias.rsplit(".", 1)[-1]
        if alias == qualified or qualified.endswith("." + alias):
            score += 8.0
            matches.append(alias)
        elif tail and tail in {short_name, signature_name}:
            score += 7.0
            matches.append(tail)
    return score, sorted(set(matches))


def score_record(record: dict[str, Any], query: str, fields: list[str]) -> tuple[float, dict[str, Any]]:
    """Score a record against a query and return (score, match_explanation)."""
    query_terms = tokens(query)
    if not query_terms:
        return 0.0, {"matched_terms": [], "matched_fields": [], "exact_matches": [], "partial_matches": []}

    hay = " ".join(normalize_text(record.get(f)) for f in fields).lower()
    score = 0.0
    match_details = {
        "matched_terms": [],
        "matched_fields": [],
        "exact_matches": [],
        "partial_matches": []
    }

    for term in query_terms:
        term_in_any_field = False
        for field in fields:
            field_value = normalize_text(record.get(field)).lower()
            if term in field_value:
                term_in_any_field = True
                if field not in match_details["matched_fields"]:
                    match_details["matched_fields"].append(field)

        if term_in_any_field:
            match_details["matched_terms"].append(term)
            score += 1.0

            # Check for exact word boundary match
            for field in fields:
                field_value = normalize_text(record.get(field)).lower()
                if re.search(rf"\b{re.escape(term)}\b", field_value):
                    match_details["exact_matches"].append({"term": term, "field": field})
                    score += 0.5
                    break
            else:
                match_details["partial_matches"].append(term)

    # Generate human-readable explanation
    explanations = []
    if match_details["exact_matches"]:
        exact_fields = set(m["field"] for m in match_details["exact_matches"])
        exact_terms = set(m["term"] for m in match_details["exact_matches"])
        explanations.append(f"Exact match for terms [{', '.join(exact_terms)}] in fields: {', '.join(exact_fields)}")
    if match_details["partial_matches"]:
        explanations.append(f"Partial match for terms: {', '.join(match_details['partial_matches'])}")

    match_details["explanation"] = "; ".join(explanations) if explanations else "No query terms matched"
    return score, match_details


def capability_keyword_boost(capability_id: str, query: str) -> tuple[float, list[str]]:
    """Calculate keyword boost score and return (score, matched_keywords)."""
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
    matched = [term for term in boosts.get(capability_id, []) if term in q]
    total_score = len(matched) * weight
    boost_explanation = []
    if matched:
        boost_explanation.append(f"Category keyword boost: matched {len(matched)} terms from {capability_id} category: {', '.join(matched)} (weight: {weight})")
    return total_score, boost_explanation


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
                sm_match = re.search(r'sm_[0-9a-z]+', combined)
                if sm_match:
                    suggested, confidence = f"cuda -arch={sm_match.group(0)}", 0.85
                else:
                    suggested, confidence = "cuda", 0.55
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
        score, match_details = score_record(rec, query, ["capability_id", "summary", "primary_symbols", "related_patterns", "when_to_use", "device_adaptation"])
        boost_score, boost_explanation = capability_keyword_boost(cap_id, query)
        score += boost_score

        # Build match reason
        match_reasons = []
        if match_details.get("explanation"):
            match_reasons.append(match_details["explanation"])
        match_reasons.extend(boost_explanation)

        rec_with_match = dict(rec)
        rec_with_match["_match_reason"] = "; ".join(match_reasons) if match_reasons else "Returned all results (empty query)"
        rec_with_match["_relevance_score"] = round(score, 2)
        rec_with_match["_matched_terms"] = match_details.get("matched_terms", [])
        rec_with_match["_matched_fields"] = match_details.get("matched_fields", [])

        if score > 0 or not query:
            scored.append((score, rec_with_match))
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
            "match_reason": rec.get("_match_reason"),
            "relevance_score": rec.get("_relevance_score"),
            "matched_terms": rec.get("_matched_terms"),
            "matched_fields": rec.get("_matched_fields"),
        })
    return {"status": "passed", "results": results}


def capability_related_pattern_ids(root: Path, capability_id: str) -> list[str] | None:
    """Return the curated pattern IDs linked from a capability record."""
    if not capability_id:
        return None
    cap_doc = load_json(root, "capability_map.json")
    records = cap_doc.get("capabilities", [])
    if not isinstance(records, list):
        return []
    for rec in records:
        if not isinstance(rec, dict):
            continue
        if normalize_text(rec.get("capability_id")) != capability_id:
            continue
        related = rec.get("related_patterns") or []
        if not isinstance(related, list):
            return []
        return [normalize_text(pattern_id) for pattern_id in related if normalize_text(pattern_id)]
    return []


def search_patterns(args: dict[str, Any]) -> dict[str, Any]:
    root = workspace_root(args.get("workspace_path"))
    query = normalize_text(args.get("query"))
    category = normalize_text(args.get("category")).lower()
    task_family = normalize_text(args.get("task_family")).lower()
    capability_id = normalize_text(args.get("capability_id"))
    related_pattern_ids = capability_related_pattern_ids(root, capability_id)
    related_pattern_set = set(related_pattern_ids or [])
    records = load_jsonl(root, "patterns.jsonl")
    scored = []
    for rec in records:
        if category and category not in normalize_text(rec.get("category")).lower():
            continue
        if task_family and task_family not in normalize_text(rec.get("task_family")).lower():
            continue
        pattern_id = normalize_text(rec.get("pattern_id"))
        if capability_id and pattern_id not in related_pattern_set:
            continue
        score, match_details = score_record(rec, query + " " + capability_id, ["pattern_id", "pattern_name", "category", "task_family", "summary", "required_symbols", "related_usage_patterns", "device_strategy"])
        if capability_id:
            score += 3.0

        # Build match reason
        match_reasons = []
        if match_details.get("explanation"):
            match_reasons.append(match_details["explanation"])
        if capability_id:
            match_reasons.append(f"Filtered by capability_id via capability_map.related_patterns: {capability_id}")
        if category:
            match_reasons.append(f"Filtered by category: {category}")
        if task_family:
            match_reasons.append(f"Filtered by task_family: {task_family}")

        rec_with_match = dict(rec)
        rec_with_match["_match_reason"] = "; ".join(match_reasons) if match_reasons else "Returned all results (empty query)"
        rec_with_match["_relevance_score"] = round(score, 2)
        rec_with_match["_matched_terms"] = match_details.get("matched_terms", [])
        rec_with_match["_matched_fields"] = match_details.get("matched_fields", [])

        if score > 0 or not query or capability_id:
            scored.append((score, rec_with_match))
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
            "match_reason": rec.get("_match_reason"),
            "relevance_score": rec.get("_relevance_score"),
            "matched_terms": rec.get("_matched_terms"),
            "matched_fields": rec.get("_matched_fields"),
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
        score, match_details = score_record(rec, query + " " + pattern_id + " " + symbols, ["usage_id", "scenario", "goal", "ordered_steps", "symbols_used", "source_files", "device_execution_notes"])

        # Build match reason
        match_reasons = []
        if match_details.get("explanation"):
            match_reasons.append(match_details["explanation"])
        if pattern_id:
            match_reasons.append(f"Pattern ID context: {pattern_id}")
        if symbols:
            match_reasons.append(f"Symbols context: {symbols}")

        rec_with_match = dict(rec)
        rec_with_match["_match_reason"] = "; ".join(match_reasons) if match_reasons else "Returned all results (empty query)"
        rec_with_match["_relevance_score"] = round(score, 2)
        rec_with_match["_matched_terms"] = match_details.get("matched_terms", [])
        rec_with_match["_matched_fields"] = match_details.get("matched_fields", [])

        if score > 0 or not query:
            scored.append((score, rec_with_match))
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
            "match_reason": rec.get("_match_reason"),
            "relevance_score": rec.get("_relevance_score"),
            "matched_terms": rec.get("_matched_terms"),
            "matched_fields": rec.get("_matched_fields"),
        })
    return {"status": "passed", "results": results}


def lookup_apis(args: dict[str, Any]) -> dict[str, Any]:
    root = workspace_root(args.get("workspace_path"))
    query = normalize_text(args.get("query"))
    symbols = normalize_text(args.get("symbols"))
    symbol_aliases = api_symbol_aliases(args.get("symbols"))
    visibility = normalize_text(args.get("visibility")).lower()
    module = normalize_text(args.get("module")).lower()
    records = load_jsonl(root, "apis.jsonl")
    scored = []
    has_lookup_query = bool(query or symbols or symbol_aliases)
    for rec in records:
        if visibility and visibility != normalize_text(rec.get("visibility")).lower():
            continue
        if module and module not in normalize_text(rec.get("module")).lower():
            continue
        score, match_details = score_record(
            rec,
            query + " " + symbols + " " + " ".join(symbol_aliases),
            ["qualified_name", "signature", "docstring", "short_summary", "operator_relevance", "module"],
        )
        exact_boost, exact_matches = api_exact_symbol_boost(rec, symbol_aliases)
        score += exact_boost

        # Build match reason
        match_reasons = []
        if match_details.get("explanation"):
            match_reasons.append(match_details["explanation"])
        if exact_matches:
            match_reasons.append(f"Exact API symbol match: {', '.join(exact_matches)}")
        if visibility:
            match_reasons.append(f"Filtered by visibility: {visibility}")
        if module:
            match_reasons.append(f"Filtered by module: {module}")
        if symbols:
            match_reasons.append(f"Symbols context: {symbols}")

        rec_with_match = dict(rec)
        rec_with_match["_match_reason"] = "; ".join(match_reasons) if match_reasons else "Returned all results (empty query)"
        rec_with_match["_relevance_score"] = round(score, 2)
        matched_terms = []
        for term in match_details.get("matched_terms", []):
            if term not in matched_terms:
                matched_terms.append(term)
        for term in exact_matches:
            if term not in matched_terms:
                matched_terms.append(term)
        rec_with_match["_matched_terms"] = matched_terms
        rec_with_match["_matched_fields"] = match_details.get("matched_fields", [])

        if score > 0 or not has_lookup_query:
            scored.append((score, rec_with_match))
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
            "match_reason": rec.get("_match_reason"),
            "relevance_score": rec.get("_relevance_score"),
            "matched_terms": rec.get("_matched_terms"),
            "matched_fields": rec.get("_matched_fields"),
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
        score, match_details = score_record(rec, query + " " + capability_id + " " + pattern_id + " " + symbols, ["chunk_id", "symbols", "summary", "why_it_matters", "related_capabilities", "related_patterns", "device_notes"])

        # Capability and pattern boosts
        boost_reasons = []
        if capability_id and capability_id in normalize_text(rec.get("related_capabilities")):
            score += 2
            boost_reasons.append(f"Capability match boost (+2): {capability_id}")
        if pattern_id and pattern_id in normalize_text(rec.get("related_patterns")):
            score += 2
            boost_reasons.append(f"Pattern match boost (+2): {pattern_id}")

        # Build match reason
        match_reasons = []
        if match_details.get("explanation"):
            match_reasons.append(match_details["explanation"])
        match_reasons.extend(boost_reasons)
        if symbols:
            match_reasons.append(f"Symbols context: {symbols}")

        rec_with_match = dict(rec)
        rec_with_match["_match_reason"] = "; ".join(match_reasons) if match_reasons else "Returned all results (empty query)"
        rec_with_match["_relevance_score"] = round(score, 2)
        rec_with_match["_matched_terms"] = match_details.get("matched_terms", [])
        rec_with_match["_matched_fields"] = match_details.get("matched_fields", [])

        if score > 0 or not query:
            scored.append((score, rec_with_match))
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
            "match_reason": rec.get("_match_reason"),
            "relevance_score": rec.get("_relevance_score"),
            "matched_terms": rec.get("_matched_terms"),
            "matched_fields": rec.get("_matched_fields"),
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
        elif query:
            score, _ = score_record(n, query, ["id", "label", "type", "attrs"])
            if score > 0:
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
        elif query:
            score, _ = score_record(e, query, ["source", "target", "edge_type"])
            if score > 0:
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


def search_troubleshooting(args: dict[str, Any]) -> dict[str, Any]:
    """Search troubleshooting knowledge base for common issues and solutions."""
    root = workspace_root(args.get("workspace_path"))
    query = normalize_text(args.get("query"))
    error_message = normalize_text(args.get("error_message"))
    category = normalize_text(args.get("category")).lower()
    severity = normalize_text(args.get("severity")).lower()

    troubleshooting_path = knowledge_dir(root) / "troubleshooting.jsonl"

    if not troubleshooting_path.is_file():
        return {
            "status": "failed",
            "error": "troubleshooting.jsonl not found in knowledge base",
            "results": []
        }

    records, errors = parse_jsonl(troubleshooting_path)
    if errors:
        return {
            "status": "failed",
            "error": f"Cannot parse troubleshooting.jsonl: {errors[0]}",
            "results": []
        }
    scored = []

    for rec in records:
        # Filter by category if specified
        if category and category != normalize_text(rec.get("category")).lower():
            continue
        # Filter by severity if specified
        if severity and severity != normalize_text(rec.get("severity")).lower():
            continue

        # Score against query and error message
        search_query = query + " " + error_message
        score, match_details = score_record(rec, search_query, [
            "title", "description", "error_patterns", "solution",
            "category", "related_symbols", "issue_id"
        ])

        # Bonus for exact error pattern matches
        error_patterns = rec.get("error_patterns", [])
        if isinstance(error_patterns, list):
            for pattern in error_patterns:
                pattern_norm = normalize_text(pattern).lower()
                query_norm = search_query.lower()
                if pattern_norm and pattern_norm in query_norm:
                    score += 3.0  # Higher weight for error message matches

        # Build match reason
        match_reasons = []
        if match_details.get("explanation"):
            match_reasons.append(match_details["explanation"])
        if category:
            match_reasons.append(f"Filtered by category: {category}")
        if severity:
            match_reasons.append(f"Filtered by severity: {severity}")

        rec_with_match = dict(rec)
        rec_with_match["_match_reason"] = "; ".join(match_reasons) if match_reasons else "Returned all results (empty query)"
        rec_with_match["_relevance_score"] = round(score, 2)
        rec_with_match["_matched_terms"] = match_details.get("matched_terms", [])

        if score > 0 or not query:
            scored.append((score, rec_with_match))

    scored.sort(key=lambda x: (x[0], {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(x[1].get("severity", "low"), 0)), reverse=True)
    results = []
    for rec in limit_results([r for _, r in scored], args.get("max_results")):
        results.append({
            "issue_id": rec.get("issue_id"),
            "title": rec.get("title"),
            "category": rec.get("category"),
            "severity": rec.get("severity"),
            "description": rec.get("description"),
            "error_patterns": rec.get("error_patterns"),
            "solution": rec.get("solution"),
            "example_fix": rec.get("example_fix"),
            "related_symbols": rec.get("related_symbols"),
            "evidence": rec.get("evidence"),
            "match_reason": rec.get("_match_reason"),
            "relevance_score": rec.get("_relevance_score"),
            "matched_terms": rec.get("_matched_terms"),
        })

    return {"status": "passed", "results": results}


def validate_operator_code(args: dict[str, Any]) -> dict[str, Any]:
    """Validate generated TileLang operator code for syntax, structure, and common issues.

    This performs static analysis without requiring TileLang to be installed.
    """
    code = normalize_text(args.get("code", ""))
    target = normalize_text(args.get("target", "cuda"))
    run_static_check = args.get("run_static_check", True)

    if not code or len(code.strip()) < 10:
        return {
            "status": "failed",
            "valid": False,
            "error": "Code is empty or too short",
            "checks": []
        }

    checks = []
    warnings = []
    errors = []
    tree = None

    import ast

    def dotted_name(node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            prefix = dotted_name(node.value)
            return f"{prefix}.{node.attr}" if prefix else node.attr
        return ""

    def decorator_name(node: ast.AST) -> str:
        if isinstance(node, ast.Call):
            return dotted_name(node.func)
        return dotted_name(node)

    def is_tilelang_kernel_function(node: ast.AST) -> bool:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return False
        decorators = {decorator_name(d) for d in node.decorator_list}
        return bool(decorators & {"tilelang.jit", "T.prim_func", "tl.jit", "jit", "prim_func"})

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        if run_static_check:
            errors.append(f"Python syntax error: {e.msg} at line {e.lineno}")
            checks.append({
                "check": "python_syntax",
                "status": "failed",
                "message": f"Syntax error: {e.msg}",
                "line": e.lineno
            })

    # 1. Check for basic structure
    if "@tilelang.jit" not in code and "@jit" not in code:
        warnings.append("Missing @tilelang.jit decorator - code may not compile as a TileLang kernel")

    # 2. Check for Tensor declaration pattern
    if "T.Tensor" not in code and "Tensor" not in code:
        warnings.append("No T.Tensor declarations found - this may not be a complete TileLang operator")

    # 3. Check for imports
    has_tilelang_import = "import tilelang" in code or "from tilelang" in code
    has_t_alias = "import tilelang.language as T" in code or "from tilelang import language as T" in code
    if tree is not None:
        has_tilelang_import = False
        has_t_alias = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "tilelang" or alias.name.startswith("tilelang."):
                        has_tilelang_import = True
                    if alias.name == "tilelang.language" and alias.asname == "T":
                        has_t_alias = True
            elif isinstance(node, ast.ImportFrom):
                if node.module == "tilelang":
                    has_tilelang_import = True
                    if any(alias.name == "language" and alias.asname == "T" for alias in node.names):
                        has_t_alias = True
                elif node.module == "tilelang.language":
                    has_tilelang_import = True

    if not has_tilelang_import:
        warnings.append("Missing 'import tilelang' or 'from tilelang ...' statement")
    if "T." in code and not has_t_alias:
        warnings.append("Using T.* without importing tilelang.language as T")

    # 4. Check for common anti-patterns inside TileLang kernel functions only.
    if tree is not None:
        anti_patterns = {
            "print": "Python print() inside TileLang kernels will not work - use T.print() if available",
            "list": "Python list() inside TileLang kernels may not lower - use T.Tensor or T.alloc_* buffers",
            "dict": "Python dict() inside TileLang kernels may not lower",
            "range": "Python range() inside TileLang kernels may not lower - use T.serial, T.Pipelined, T.Parallel, or static host loops",
        }
        seen_warnings: set[str] = set()
        for fn in [n for n in ast.walk(tree) if is_tilelang_kernel_function(n)]:
            for node in ast.walk(fn):
                if not isinstance(node, ast.Call):
                    continue
                call_name = dotted_name(node.func)
                if call_name in anti_patterns and call_name not in seen_warnings:
                    warnings.append(f"Potential issue: {anti_patterns[call_name]}")
                    seen_warnings.add(call_name)

    # 5. Check for kernel structure
    has_kernel = "T.Kernel" in code or "with Kernel" in code
    has_shared = "T.alloc_shared" in code or "alloc_shared" in code
    has_pipelined = "T.Pipelined" in code or "Pipelined" in code

    checks.append({
        "check": "kernel_structure",
        "status": "info",
        "message": "Kernel structure analysis",
        "details": {
            "has_T_Kernel": has_kernel,
            "has_shared_memory": has_shared,
            "has_pipelining": has_pipelined,
        }
    })

    # 6. Check for device-specific features
    device_features = []
    if "sm_90" in code or "H100" in code or "hopper" in code.lower():
        device_features.append("H100/Hopper specific features detected")
    if "sm_80" in code or "A100" in code or "ampere" in code.lower():
        device_features.append("A100/Ampere specific features detected")
    if "wgmma" in code.lower():
        device_features.append("WGMMA tensor intrinsics detected - Hopper+ only")
    if "TMA" in code or "tma_copy" in code.lower():
        device_features.append("TMA memory operations detected - Hopper+ only")

    if device_features:
        checks.append({
            "check": "device_features",
            "status": "info",
            "message": "Device-specific features detected",
            "details": device_features
        })

    # 7. Syntax validation (basic Python syntax check)
    if run_static_check and tree is not None:
            checks.append({
                "check": "python_syntax",
                "status": "passed",
                "message": "Python syntax is valid"
            })

    # 8. Check for common GEMM patterns
    gemm_indicators = ["gemm", "matmul", "A[i, k]", "B[k, j]", "C[i, j]"]
    gemm_score = sum(1 for ind in gemm_indicators if ind.lower() in code.lower())
    if gemm_score >= 2:
        checks.append({
            "check": "operator_type",
            "status": "info",
            "message": f"Appears to be a GEMM-like operator (score: {gemm_score}/4)"
        })

    # 9. Check for proper output handling
    if "out_idx" in code:
        checks.append({
            "check": "output_handling",
            "status": "info",
            "message": "out_idx specified in @tilelang.jit decorator"
        })

    # Overall result
    overall_status = "passed" if not errors else "failed"
    if warnings and not errors:
        overall_status = "warnings"

    return {
        "status": overall_status,
        "valid": len(errors) == 0,
        "checks_performed": checks,
        "warnings": warnings,
        "errors": errors,
        "recommendations": [
            "Always test compiled kernels with small inputs before benchmarking",
            "Validate numerical correctness against reference implementation",
            "Check that tensor shapes and dtypes match between kernel and inputs",
        ],
        "code_size": len(code),
        "target_device": target
    }


def operator_development_wizard(args: dict[str, Any]) -> dict[str, Any]:
    """Step-by-step wizard to guide operator development.

    This tool provides a guided workflow that walks the user through
    each step of TileLang operator development, from intent to validation.
    """
    current_step = args.get("current_step", 1)
    operator_intent = normalize_text(args.get("operator_intent", ""))
    device_profile = args.get("device_profile", {})
    workspace_path = args.get("workspace_path")
    tilelang_source_path = args.get("tilelang_source_path")

    # Define the workflow steps
    workflow_steps = {
        1: {
            "step_id": 1,
            "title": "Validate Workspace",
            "description": "Check that you have a valid TileLang workspace and knowledge base",
            "action_required": "Call inspect_tilelang_workspace and validate_knowledge_base",
            "completion_criteria": "Both workspace and knowledge base validation pass",
            "tools_to_use": ["inspect_tilelang_workspace", "validate_knowledge_base"]
        },
        2: {
            "step_id": 2,
            "title": "Define Operator Intent",
            "description": "Clearly define what operator you want to develop",
            "action_required": "Describe the operator: type (GEMM, attention, etc.), features, expected input/output shapes",
            "completion_criteria": "Operator intent is clearly defined and contains operator type description",
            "tools_to_use": []
        },
        3: {
            "step_id": 3,
            "title": "Normalize Device Profile",
            "description": "Identify the target device and architecture",
            "action_required": "Specify vendor (NVIDIA/AMD/CPU/Apple), model (A100/H100/MI300/etc.), and target",
            "completion_criteria": "Device profile is normalized with confidence score",
            "tools_to_use": ["normalize_device_profile"]
        },
        4: {
            "step_id": 4,
            "title": "Find Capability Match",
            "description": "Search for matching capabilities in the knowledge base",
            "action_required": "Use search_capabilities to find the right capability category",
            "completion_criteria": "At least one capability candidate found with relevance score > 0",
            "tools_to_use": ["search_capabilities"]
        },
        5: {
            "step_id": 5,
            "title": "Select Operator Pattern",
            "description": "Find and select the most appropriate operator pattern",
            "action_required": "Use search_patterns with capability ID to find matching patterns",
            "completion_criteria": "Pattern candidates available with device strategy information",
            "tools_to_use": ["search_patterns"]
        },
        6: {
            "step_id": 6,
            "title": "Review Usage Patterns",
            "description": "Understand how to instantiate, compile, and test the operator",
            "action_required": "Use search_usage_patterns to find example workflows for your pattern",
            "completion_criteria": "Usage patterns retrieved with ordered_steps and prerequisites",
            "tools_to_use": ["search_usage_patterns"]
        },
        7: {
            "step_id": 7,
            "title": "Confirm API Signatures",
            "description": "Verify the APIs you'll need to use",
            "action_required": "Use lookup_apis to confirm signatures for symbols required by the pattern",
            "completion_criteria": "Required API symbols are found with visibility and module info",
            "tools_to_use": ["lookup_apis"]
        },
        8: {
            "step_id": 8,
            "title": "Source Chunk Reference",
            "description": "Get concrete source code examples for reference",
            "action_required": "Use get_source_chunks for pattern-specific code examples",
            "completion_criteria": "Source chunks retrieved with device notes",
            "tools_to_use": ["get_source_chunks"]
        },
        9: {
            "step_id": 9,
            "title": "Build Retrieval Plan",
            "description": "Assemble all retrieved information into a plan",
            "action_required": "Call build_operator_retrieval_plan to synthesize findings",
            "completion_criteria": "Complete retrieval plan generated with candidates and confidence",
            "tools_to_use": ["build_operator_retrieval_plan"]
        },
        10: {
            "step_id": 10,
            "title": "Generate Code",
            "description": "Generate the TileLang operator code",
            "action_required": "Write the operator code using patterns and APIs from previous steps",
            "completion_criteria": "Code generated with proper decorators and structure",
            "tools_to_use": []
        },
        11: {
            "step_id": 11,
            "title": "Validate Generated Code",
            "description": "Static analysis of the generated code",
            "action_required": "Call validate_operator_code to check for issues",
            "completion_criteria": "Code passes validation with no errors (warnings are OK)",
            "tools_to_use": ["validate_operator_code"]
        },
        12: {
            "step_id": 12,
            "title": "Completion",
            "description": "Operator development workflow complete!",
            "action_required": "Review the generated operator and validation results",
            "completion_criteria": "All previous steps completed successfully",
            "tools_to_use": []
        }
    }

    # Calculate progress
    total_steps = len(workflow_steps)
    progress_percent = round((current_step - 1) / total_steps * 100, 1)

    # Get current step info
    current = workflow_steps.get(current_step, workflow_steps[1])

    # Get next steps
    next_steps = []
    for i in range(current_step + 1, min(current_step + 4, total_steps + 1)):
        if i in workflow_steps:
            next_steps.append({
                "step_id": workflow_steps[i]["step_id"],
                "title": workflow_steps[i]["title"]
            })

    # Auto-complete steps where possible
    auto_completed = []
    if current_step == 1 and workspace_path:
        # Auto-run workspace validation
        validation_args = {
            "workspace_path": workspace_path,
            "tilelang_source_path": tilelang_source_path,
        }
        workspace_result = inspect_workspace(validation_args)
        kb_result = validate_knowledge(validation_args)
        auto_completed.append({
            "step_id": 1,
            "results": {
                "workspace": workspace_result,
                "knowledge_base": kb_result
            },
            "status": "completed" if workspace_result["status"] == "passed" and kb_result["status"] == "passed" else "needs_attention"
        })

    if current_step == 3 and device_profile:
        # Auto-run device normalization
        device_result = normalize_device(device_profile if isinstance(device_profile, dict) else {"model": normalize_text(device_profile)})
        auto_completed.append({
            "step_id": 3,
            "results": device_result,
            "status": "completed" if device_result["status"] == "passed" else "needs_attention"
        })

    return {
        "status": "in_progress" if current_step < total_steps else "completed",
        "current_step": current_step,
        "current_step_info": current,
        "total_steps": total_steps,
        "progress_percent": progress_percent,
        "next_steps": next_steps,
        "auto_completed": auto_completed,
        "operator_intent": operator_intent,
        "device_profile": device_profile,
        "tips": [
            "Complete each step before moving to the next",
            "Use the tools listed in each step to gather information",
            "If you get stuck, use search_troubleshooting to find solutions",
            "Review patterns from similar operators before writing code"
        ]
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
    "search_troubleshooting": search_troubleshooting,
    "validate_operator_code": validate_operator_code,
    "operator_development_wizard": operator_development_wizard,
}


def tool_definitions() -> list[dict[str, Any]]:
    # Base properties for workspace tools
    # Note: tilelang_source_path enables dual-workspace mode:
    # - operator_workspace: where your operator code lives
    # - tilelang_source: where TileLang source repository is (separate)
    base_props = {
        "workspace_path": {
            "type": "string",
            "description": "Operator workspace root (where your operator code lives)."
        },
        "tilelang_source_path": {
            "type": "string",
            "description": "TileLang source repository root. Falls back to TILELANG_SOURCE_PATH env var or workspace_path (backward compatibility)."
        }
    }

    return [
        {"name": "inspect_tilelang_workspace", "description": "Validate TileLang repository and tilelang_knowledge presence. Supports dual-workspace mode for independent operator development.", "inputSchema": {"type": "object", "properties": base_props}},
        {"name": "validate_knowledge_base", "description": "Validate required delivery files and parse JSON/JSONL.", "inputSchema": {"type": "object", "properties": base_props}},
        {"name": "normalize_device_profile", "description": "Normalize vendor/model/target for device-aware TileLang operator planning.", "inputSchema": {"type": "object", "properties": {"vendor": {"type": "string"}, "model": {"type": "string"}, "target": {"type": "string"}, "arch": {"type": "string"}}}},
        {"name": "search_capabilities", "description": "Search capability_map.json for operator capabilities.", "inputSchema": {"type": "object", "properties": {**base_props, "query": {"type": "string"}, "max_results": {"type": "integer"}}}},
        {"name": "search_patterns", "description": "Search patterns.jsonl for operator implementation patterns.", "inputSchema": {"type": "object", "properties": {**base_props, "query": {"type": "string"}, "category": {"type": "string"}, "task_family": {"type": "string"}, "capability_id": {"type": "string"}, "max_results": {"type": "integer"}}}},
        {"name": "search_usage_patterns", "description": "Search usage_patterns.jsonl for example workflows.", "inputSchema": {"type": "object", "properties": {**base_props, "query": {"type": "string"}, "pattern_id": {"type": "string"}, "symbols": {"type": "array", "items": {"type": "string"}}, "max_results": {"type": "integer"}}}},
        {"name": "lookup_apis", "description": "Search apis.jsonl for TileLang API symbols and signatures.", "inputSchema": {"type": "object", "properties": {**base_props, "query": {"type": "string"}, "symbols": {"type": "array", "items": {"type": "string"}}, "visibility": {"type": "string"}, "module": {"type": "string"}, "max_results": {"type": "integer"}}}},
        {"name": "get_source_chunks", "description": "Retrieve source fallback chunks from TileLang source.", "inputSchema": {"type": "object", "properties": {**base_props, "query": {"type": "string"}, "capability_id": {"type": "string"}, "pattern_id": {"type": "string"}, "symbols": {"type": "array", "items": {"type": "string"}}, "max_results": {"type": "integer"}}}},
        {"name": "trace_semantic_graph", "description": "Trace semantic graph nodes and edges.", "inputSchema": {"type": "object", "properties": {**base_props, "node_id": {"type": "string"}, "query": {"type": "string"}, "edge_type": {"type": "string"}, "max_results": {"type": "integer"}}}},
        {"name": "build_operator_retrieval_plan", "description": "Build a structured retrieval plan for an operator intent. Supports dual-workspace mode.", "inputSchema": {"type": "object", "properties": {**base_props, "operator_intent": {"type": "string"}, "device_profile": {"type": "object"}}}},
        {"name": "search_troubleshooting", "description": "Search troubleshooting knowledge base for common issues, errors, and solutions.", "inputSchema": {"type": "object", "properties": {**base_props, "query": {"type": "string"}, "error_message": {"type": "string", "description": "The actual error message to match"}, "category": {"type": "string", "description": "Issue category: compilation, runtime, performance, api, device, installation, pattern"}, "severity": {"type": "string", "description": "Issue severity: low, medium, high, critical"}, "max_results": {"type": "integer"}}}},
        {"name": "validate_operator_code", "description": "Static analysis of TileLang operator code for syntax, structure, and common issues.", "inputSchema": {"type": "object", "properties": {"code": {"type": "string", "description": "The generated TileLang operator code to validate"}, "target": {"type": "string", "description": "Target device: cuda, hip, cpu, metal, webgpu"}, "run_static_check": {"type": "boolean", "description": "Whether to run Python AST syntax check"}}}},
        {"name": "operator_development_wizard", "description": "Step-by-step guided workflow for TileLang operator development from intent to validation. Supports dual-workspace mode.", "inputSchema": {"type": "object", "properties": {"current_step": {"type": "integer", "description": "Current step in the workflow (1-12)"}, "operator_intent": {"type": "string", "description": "Description of the operator to develop"}, "device_profile": {"type": "object", "description": "Device profile information"}, **base_props}}},
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
        except McpError as exc:
            err = {"error": str(exc)}
            msg_id = None
            try:
                msg_id = payload.get("id") if isinstance(payload, dict) else None  # type: ignore[name-defined]
            except Exception:
                pass
            respond(msg_id, {"content": [{"type": "text", "text": json.dumps(err, ensure_ascii=False, indent=2)}], "isError": True})
        except Exception as exc:
            err = {"error": f"Internal error: {type(exc).__name__}"}
            msg_id = None
            try:
                msg_id = payload.get("id") if isinstance(payload, dict) else None  # type: ignore[name-defined]
            except Exception:
                pass
            respond(msg_id, {"content": [{"type": "text", "text": json.dumps(err, ensure_ascii=False, indent=2)}], "isError": True})


def run_check() -> dict[str, Any]:
    """Deep self-check: verify knowledge base, parse files, and test a tool call."""
    result: dict[str, Any] = {"serverInfo": SERVER_INFO, "checks": []}

    # 1. Knowledge base discovery
    kdir = BUILTIN_KNOWLEDGE
    if kdir.is_dir():
        result["checks"].append({"name": "knowledge_base_found", "status": "passed", "path": str(kdir)})
    else:
        result["checks"].append({"name": "knowledge_base_found", "status": "failed", "error": f"Not found: {kdir}"})
        result["status"] = "failed"
        return result

    # 2. Required files
    missing = [f for f in KNOWLEDGE_REQUIRED if not (kdir / f).is_file()]
    if missing:
        result["checks"].append({"name": "required_files", "status": "failed", "missing": missing})
    else:
        result["checks"].append({"name": "required_files", "status": "passed"})

    # 3. JSON/JSONL parsing
    parse_errors = {}
    for name in JSON_FILES:
        path = kdir / name
        if path.is_file():
            _, err = parse_json(path)
            if err:
                parse_errors[name] = err
    for name in JSONL_FILES:
        path = kdir / name
        if path.is_file():
            _, errors = parse_jsonl(path)
            if errors:
                parse_errors[name] = errors[:3]
    if parse_errors:
        result["checks"].append({"name": "parse_files", "status": "failed", "errors": parse_errors})
    else:
        result["checks"].append({"name": "parse_files", "status": "passed"})

    # 4. Tool smoke test: call normalize_device_profile (no knowledge base needed)
    try:
        tool_result = normalize_device({"vendor": "nvidia", "model": "H100", "target": "cuda"})
        if tool_result.get("status") in ("passed", "constrained"):
            result["checks"].append({"name": "tool_call", "status": "passed", "tool": "normalize_device_profile"})
        else:
            result["checks"].append({"name": "tool_call", "status": "failed", "error": "Unexpected status"})
    except Exception as exc:
        result["checks"].append({"name": "tool_call", "status": "failed", "error": str(exc)})

    # 5. Capability search against built-in knowledge base
    try:
        cap_result = search_capabilities({"query": "gemm", "max_results": 1})
        if cap_result.get("status") == "passed" and cap_result.get("results"):
            result["checks"].append({"name": "capability_search", "status": "passed"})
        else:
            result["checks"].append({"name": "capability_search", "status": "failed", "error": "No results"})
    except Exception as exc:
        result["checks"].append({"name": "capability_search", "status": "failed", "error": str(exc)})

    all_passed = all(c["status"] == "passed" for c in result["checks"])
    result["status"] = "passed" if all_passed else "failed"
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="TileLang operator knowledge MCP server.")
    parser.add_argument("--check", action="store_true", help="Run a deep self-check and exit.")
    args = parser.parse_args()
    if args.check:
        result = run_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    run_server()


if __name__ == "__main__":
    main()
