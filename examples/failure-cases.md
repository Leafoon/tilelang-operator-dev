# Example: Failure Cases

This example shows how the skill handles error conditions.

## Case 1: Missing Knowledge Base

**User Request**: "Write an attention kernel"

**Workflow**:
```
Call: inspect_tilelang_workspace(workspace_path="/some/path")
Result: status=failed, missing_knowledge_files=["tilelang_knowledge/"]
```

**Output**:
```
Cannot safely generate a TileLang operator yet.

Missing or invalid:
- tilelang_knowledge/ directory not found

Required fix:
- Place the TileLang repository at the active workspace root.
- Restore/generate tilelang_knowledge/ with retrieval_plan.md, capability_map.json,
  patterns.jsonl, usage_patterns.jsonl, apis.jsonl, source_chunks.jsonl,
  semantic_graph.json, semantic_graph.mmd, manifest.json, and README.md.
- Re-invoke the tilelang-operator-dev skill.
```

## Case 2: Not a TileLang Repository

**User Request**: "Write a CUDA kernel"

**Workflow**:
```
Call: inspect_tilelang_workspace(workspace_path="/random/dir")
Result: status=failed, is_tilelang_repo=false, missing_repo_indicators=["tilelang/__init__.py", ...]
```

**Output**:
```
Cannot safely generate a TileLang operator yet.

Missing or invalid:
- Not a TileLang repository (missing tilelang/__init__.py)

Required fix:
- Switch to a TileLang repository workspace.
- Re-invoke the tilelang-operator-dev skill.
```

## Case 3: Parse Error

**User Request**: "Search for reduction patterns"

**Workflow**:
```
Call: validate_knowledge_base()
Result: status=failed, parse_errors={"patterns.jsonl": "line 42: Invalid JSON"}
```

**Output**:
```
Cannot safely generate a TileLang operator yet.

Missing or invalid:
- patterns.jsonl has parse errors: line 42: Invalid JSON

Required fix:
- Fix the JSON/JSONL files in tilelang_knowledge/.
- Re-invoke the tilelang-operator-dev skill.
```

## Case 4: Unknown Device

**User Request**: "Write a kernel for my custom FPGA"

**Workflow**:
```
Call: normalize_device_profile(vendor="Xilinx", model="Alveo")
Result: status=constrained, vendor=unknown
Notes: "Device vendor/model could not be mapped to a known TileLang target family."
```

**Output**:
```
Device Profile:
- Vendor: unknown
- Target: not determined
- Confidence: low

The device could not be mapped to a known TileLang target. Please provide:
- Exact target string (e.g., "cuda -arch=sm_90", "hip -mcpu=gfx940")
- Or specify if this is NVIDIA, AMD, CPU, Apple, or WebGPU
```
