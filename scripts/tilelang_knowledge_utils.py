"""Shared utilities for TileLang knowledge record parsing and validation.

Used by both the MCP server (tilelang_operator_mcp.py) and the knowledge
audit script (audit_tilelang_knowledge.py) to avoid code duplication and
ensure consistent schema handling.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SOURCE_PATH_SUFFIXES = (".py", ".pyi", ".md", ".toml", ".cc", ".h", ".hpp", ".cu", ".cuh", ".txt")


def looks_like_source_path(value: str) -> bool:
    """Heuristic: does this string look like a relative source file path?

    A source path must not contain spaces (excludes sentences like
    'see tilelang/docs/targets.md for details') and must either end with
    a known source-file extension or contain '/' (relative path).
    """
    candidate = value.strip()
    if not candidate or "\n" in candidate or " " in candidate:
        return False
    return "/" in candidate or candidate.endswith(SOURCE_PATH_SUFFIXES)


def parse_json(path: Path) -> tuple[Any | None, str | None]:
    """Parse a JSON file. Returns (data, None) or (None, error_string)."""
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, str(exc)


def parse_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    """Parse a JSONL file. Returns (records, errors)."""
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception as exc:
        return [], [str(exc)]
    for lineno, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                records.append(obj)
            else:
                errors.append(f"{path.name}:{lineno}: record is not an object")
        except Exception as exc:
            errors.append(f"{path.name}:{lineno}: {exc}")
    return records, errors


def source_line_count(path: Path) -> int:
    """Count lines in a file, ignoring encoding errors."""
    try:
        return sum(1 for _ in path.open(encoding="utf-8", errors="ignore"))
    except Exception:
        return 0


def walk_source_paths(value: Any, source: str, out: list[tuple[str, str]]) -> None:
    """Recursively collect source-relative file paths from knowledge records.

    Looks for:
    - file_path keys
    - source_files lists
    - source_lines dict keys
    - evidence strings/lists that look like source paths
    """
    if isinstance(value, dict):
        file_path = value.get("file_path")
        if isinstance(file_path, str) and file_path:
            out.append((file_path, source))
        source_files = value.get("source_files")
        if isinstance(source_files, list):
            for path in source_files:
                if isinstance(path, str) and path:
                    out.append((path, source))
        source_lines = value.get("source_lines")
        if isinstance(source_lines, dict):
            for path in source_lines:
                if isinstance(path, str) and path:
                    out.append((path, source))
        evidence = value.get("evidence")
        if isinstance(evidence, str) and looks_like_source_path(evidence):
            out.append((evidence, source))
        elif isinstance(evidence, list):
            for item in evidence:
                if isinstance(item, str) and looks_like_source_path(item):
                    out.append((item, source))
        for child in value.values():
            walk_source_paths(child, source, out)
    elif isinstance(value, list):
        for child in value:
            walk_source_paths(child, source, out)


def walk_line_ranges(value: Any, source: str, out: list[tuple[str, str, int, int]]) -> None:
    """Recursively collect source-relative line ranges from knowledge records.

    Looks for file_path + line, file_path + line_start/line_end, etc.
    """
    if isinstance(value, dict):
        file_path = value.get("file_path")
        if isinstance(file_path, str) and file_path:
            if "line" in value:
                try:
                    line = int(value["line"])
                    out.append((file_path, source, line, line))
                except Exception:
                    out.append((file_path, source, 0, 0))
            start_value = value.get("line_start") or value.get("start_line")
            if start_value is not None:
                try:
                    start = int(start_value)
                    end = int(value.get("line_end") or value.get("end_line") or start)
                    out.append((file_path, source, start, end))
                except Exception:
                    out.append((file_path, source, 0, 0))
        for child in value.values():
            walk_line_ranges(child, source, out)
    elif isinstance(value, list):
        for child in value:
            walk_line_ranges(child, source, out)
