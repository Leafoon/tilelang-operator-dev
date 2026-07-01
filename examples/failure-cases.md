# Example: Failure Cases

This example shows how the skill handles error conditions.

## Case 1: TileLang Source Not Found

**User Request**: "Write an attention kernel"

**Workflow**:
```
Call: inspect_tilelang_workspace(workspace_path="/some/path")
Result: status=failed, is_tilelang_repo=false, missing_repo_indicators=["tilelang/__init__.py", ...]
```

**Output**:
```
Cannot safely generate a TileLang operator yet.

Missing or invalid:
- TileLang source repository could not be resolved or validated

Required fix:
- Place the official TileLang repository next to the operator workspace as ../tilelang,
  or set TILELANG_SOURCE_PATH, or pass tilelang_source_path during MCP debugging.
- Re-invoke the tilelang-operator-dev skill.
```

## Case 2: Retrieval Plan Without Valid Source

**User Request**: "Write a CUDA kernel"

**Workflow**:
```
Call: build_operator_retrieval_plan(workspace_path="/random/dir", operator_intent="GEMM")
Result: status=failed, tilelang_source_valid=false
```

**Output**:
```
Cannot safely generate a TileLang operator yet.

Missing or invalid:
- Retrieval may find bundled knowledge records, but source evidence cannot be validated.

Required fix:
- Resolve a valid TileLang source checkout first.
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
- Fix the selected workspace-local `tilelang_knowledge/`, or remove it to use the bundled delivery set.
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
