#!/usr/bin/env python3
"""Audit TileLang knowledge records against a TileLang source checkout."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from tilelang_knowledge_utils import (
    SOURCE_PATH_SUFFIXES,
    looks_like_source_path,
    parse_json as read_json,
    parse_jsonl as read_jsonl,
    source_line_count as line_count,
    walk_line_ranges,
    walk_source_paths as walk_paths,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_KNOWLEDGE_DIR = REPO_ROOT / "resources" / "tilelang_knowledge"
JSON_FILES = ["capability_map.json", "semantic_graph.json", "manifest.json"]
JSONL_FILES = ["patterns.jsonl", "usage_patterns.jsonl", "apis.jsonl", "source_chunks.jsonl", "troubleshooting.jsonl"]


def audit(tilelang_source: Path, knowledge_dir: Path) -> dict[str, Any]:
    parse_errors: dict[str, list[str]] = {}
    referenced_paths: list[tuple[str, str]] = []
    line_ranges: list[tuple[str, str, int, int]] = []

    for name in JSON_FILES:
        path = knowledge_dir / name
        if not path.exists():
            continue
        obj, err = read_json(path)
        if err:
            parse_errors[name] = [err]
            continue
        walk_paths(obj, name, referenced_paths)
        walk_line_ranges(obj, name, line_ranges)

    jsonl_counts: dict[str, int] = {}
    jsonl_records: dict[str, list[dict[str, Any]]] = {}
    for name in JSONL_FILES:
        path = knowledge_dir / name
        if not path.exists():
            continue
        records, errors = read_jsonl(path)
        jsonl_records[name] = records
        jsonl_counts[name] = len(records)
        if errors:
            parse_errors[name] = errors
            continue
        for index, record in enumerate(records, 1):
            source = f"{name}:{index}"
            walk_paths(record, source, referenced_paths)
            walk_line_ranges(record, source, line_ranges)

    unique_paths = sorted({path for path, _ in referenced_paths})
    missing_refs = [
        {"file_path": path, "source": source}
        for path, source in referenced_paths
        if not (tilelang_source / path).exists()
    ]

    line_issues = []
    for rel_path, source, start, end in line_ranges:
        full_path = tilelang_source / rel_path
        if not full_path.exists():
            continue
        total = line_count(full_path)
        if start < 1 or end < start or end > total:
            line_issues.append({
                "file_path": rel_path,
                "source": source,
                "start": start,
                "end": end,
                "total_lines": total,
            })

    examples_dir = tilelang_source / "examples"
    official_examples = sorted(p.name for p in examples_dir.iterdir() if p.is_dir()) if examples_dir.is_dir() else []
    raw_covered_examples = {
        path.split("/", 2)[1]
        for path in unique_paths
        if path.startswith("examples/") and len(path.split("/")) >= 2
    }
    covered_examples = sorted(set(official_examples) & raw_covered_examples)
    missing_example_dirs = sorted(set(official_examples) - set(covered_examples))

    usage_ids = {
        rec.get("usage_id")
        for rec in jsonl_records.get("usage_patterns.jsonl", [])
        if isinstance(rec.get("usage_id"), str)
    }
    missing_usage_refs = []
    for index, record in enumerate(jsonl_records.get("patterns.jsonl", []), 1):
        related = record.get("related_usage_patterns") or []
        if not isinstance(related, list):
            continue
        for usage_id in related:
            if isinstance(usage_id, str) and usage_id not in usage_ids:
                missing_usage_refs.append({
                    "pattern_id": record.get("pattern_id"),
                    "usage_id": usage_id,
                    "source": f"patterns.jsonl:{index}",
                })

    status = "passed" if not parse_errors and not missing_refs and not line_issues and not missing_usage_refs else "failed"
    return {
        "status": status,
        "tilelang_source": str(tilelang_source),
        "knowledge_dir": str(knowledge_dir),
        "jsonl_counts": jsonl_counts,
        "referenced_path_count": len(unique_paths),
        "missing_reference_count": len(missing_refs),
        "missing_references": missing_refs[:100],
        "line_issue_count": len(line_issues),
        "line_issues": line_issues[:100],
        "missing_usage_reference_count": len(missing_usage_refs),
        "missing_usage_references": missing_usage_refs[:100],
        "parse_errors": parse_errors,
        "example_coverage": {
            "official_dir_count": len(official_examples),
            "covered_dir_count": len(covered_examples),
            "covered_dirs": covered_examples,
            "missing_dir_count": len(missing_example_dirs),
            "missing_dirs": missing_example_dirs,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit TileLang knowledge records against a TileLang source checkout.")
    parser.add_argument("--tilelang-source", required=True, help="Path to a TileLang source checkout")
    parser.add_argument("--knowledge-dir", default=str(DEFAULT_KNOWLEDGE_DIR), help="Path to tilelang_knowledge")
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    parser.add_argument("--fail-on-coverage-gaps", action="store_true", help="Return nonzero when official example directories are not covered")
    args = parser.parse_args()

    result = audit(Path(args.tilelang_source).expanduser().resolve(), Path(args.knowledge_dir).expanduser().resolve())
    if args.fail_on_coverage_gaps and result["example_coverage"]["missing_dir_count"]:
        result["status"] = "failed"

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        coverage = result["example_coverage"]
        print(f"Status: {result['status']}")
        print(f"Knowledge: {result['knowledge_dir']}")
        print(f"TileLang source: {result['tilelang_source']}")
        print(f"Referenced paths: {result['referenced_path_count']}")
        print(f"Missing references: {result['missing_reference_count']}")
        print(f"Line issues: {result['line_issue_count']}")
        print(f"Missing usage references: {result['missing_usage_reference_count']}")
        print(f"Example coverage: {coverage['covered_dir_count']}/{coverage['official_dir_count']} directories")
        if coverage["missing_dirs"]:
            print("Missing example directories:")
            for name in coverage["missing_dirs"]:
                print(f"  - {name}")
        if result["parse_errors"]:
            print("Parse errors:")
            for name, errors in result["parse_errors"].items():
                print(f"  - {name}: {errors[0]}")

    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
