# Test Cases

## Workspace Validation Tests

### Test 1: Valid TileLang Repository
- **Input**: Workspace with `tilelang/__init__.py`, `src/transform/`, `examples/`
- **Expected**: `inspect_tilelang_workspace` returns `status=passed`

### Test 2: Missing Workspace-Local tilelang_knowledge With Bundled Fallback
- **Input**: Valid TileLang repo without `tilelang_knowledge/`
- **Expected**: `inspect_tilelang_workspace` returns `status=passed`, `knowledge_source=builtin`, and `missing_knowledge_files=[]`

### Test 3: Not a TileLang Repository
- **Input**: Random directory without TileLang indicators
- **Expected**: `inspect_tilelang_workspace` returns `status=failed`, `is_tilelang_repo=false`

## Knowledge Base Validation Tests

### Test 4: Valid Knowledge Base
- **Input**: Workspace with bundled knowledge or complete workspace-local `tilelang_knowledge/`
- **Expected**: `validate_knowledge_base` returns `status=passed`, counts populated

### Test 5: Incomplete Workspace-Local Knowledge Falls Back
- **Input**: `tilelang_knowledge/` missing `patterns.jsonl`
- **Expected**: `validate_knowledge_base` uses bundled knowledge when available and returns `status=passed`, `knowledge_source=builtin`

### Test 6: Parse Error In Resolved Knowledge
- **Input**: `patterns.jsonl` with invalid JSON
- **Expected**: `validate_knowledge_base` returns `status=failed`, `parse_errors` populated

## Device Normalization Tests

### Test 7: NVIDIA H100
- **Input**: `vendor="NVIDIA", model="H100"`
- **Expected**: `vendor=NVIDIA`, `suggested_target="cuda -arch=sm_90"`, `confidence>=0.8`

### Test 8: AMD MI300X
- **Input**: `vendor="AMD", model="MI300X"`
- **Expected**: `vendor=AMD`, `confidence>=0.7`

### Test 9: Unknown Device
- **Input**: `vendor="Xilinx", model="Alveo"`
- **Expected**: `vendor=unknown`, `confidence<=0.5`

## Search Tests

### Test 10: GEMM Capability Search
- **Input**: `query="GEMM matrix multiply"`
- **Expected**: Results include `gemm_like_patterns`

### Test 11: Pattern Search with Capability Filter
- **Input**: `query="attention", capability_id="attention_like_patterns"`
- **Expected**: Results are filtered through `capability_map.related_patterns` and include attention patterns

### Test 11b: Pattern Search with Category Filter
- **Input**: `query="attention", category="attention"`
- **Expected**: Results have an attention category

### Test 12: API Lookup
- **Input**: `query="T.gemm"`
- **Expected**: Results include `T.gemm` with correct signature

## New Tools Tests

### Test 13: Troubleshooting Search
- **Input**: `query="dtype mismatch"`
- **Expected**: `search_troubleshooting` returns results with compilation issues

### Test 14: Troubleshooting Search by Category
- **Input**: `query="", category="compilation"`
- **Expected**: Results filtered to compilation category

### Test 15: Code Validation - Valid Code
- **Input**: `code="import tilelang\nimport tilelang.language as T\n\n@tilelang.jit\ndef gemm(A, B):\n    return None"`
- **Expected**: `validate_operator_code` returns `valid=True`

### Test 16: Code Validation - Empty Code
- **Input**: `code=""`
- **Expected**: `validate_operator_code` returns `valid=False`

### Test 17: Code Validation - Syntax Error
- **Input**: `code="import tilelang\ndef broken(\n    syntax error here"`
- **Expected**: `validate_operator_code` returns `status=failed` with syntax error

### Test 18: Development Wizard - Step 1
- **Input**: `current_step=1`
- **Expected**: `operator_development_wizard` returns `status="in_progress"`, `current_step=1`

### Test 19: Development Wizard with Intent
- **Input**: `current_step=1, operator_intent="GEMM kernel for H100"`
- **Expected**: Response includes `operator_intent` field

## End-to-End Tests

### Test 20: Basic GEMM Workflow
1. Validate workspace
2. Validate knowledge base
3. Normalize device (H100)
4. Search capabilities for "GEMM"
5. Search patterns for "GEMM"
6. Lookup APIs for ["T.gemm"]
7. Build retrieval plan

**Expected**: All steps succeed, final plan has `status=passed`

### Test 21: Failure Recovery
1. Validate workspace (fails - not TileLang repo)
2. Stop and report error

**Expected**: Skill stops immediately, does not attempt code generation

## Dual-Workspace Mode Tests

### Test 22: Workspace Returns New Fields
- **Input**: `inspect_tilelang_workspace`
- **Expected**: Response includes `operator_workspace_path`, `tilelang_source_path`, and `workspace_mode`

### Test 23: Knowledge Base Returns New Fields
- **Input**: `validate_knowledge_base`
- **Expected**: Response includes `operator_workspace_path`, `tilelang_source_path`, and `workspace_mode`

### Test 24: Tool Definitions Include tilelang_source_path
- **Input**: `tools/list`
- **Expected**: Key workspace tools have `tilelang_source_path` parameter

## Auto-Detection Tests

### Test 25: Auto-Detect Returns Candidates
- **Input**: `inspect_tilelang_workspace`
- **Expected**: If auto-detected, response includes `auto_detected` field

### Test 26: Multiple Candidates Reported
- **Input**: `inspect_tilelang_workspace` (when multiple TileLang sources exist)
- **Expected**: `multiple_candidates` is a list with more than 1 item

### Test 27: Hint When No TileLang Found
- **Input**: `inspect_tilelang_workspace` with non-existent path
- **Expected**: Response includes `hint` field with helpful message
