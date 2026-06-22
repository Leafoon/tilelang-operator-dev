# Test Cases

## Workspace Validation Tests

### Test 1: Valid TileLang Repository
- **Input**: Workspace with `tilelang/__init__.py`, `src/transform/`, `examples/`
- **Expected**: `inspect_tilelang_workspace` returns `status=passed`

### Test 2: Missing tilelang_knowledge
- **Input**: Valid TileLang repo without `tilelang_knowledge/`
- **Expected**: `inspect_tilelang_workspace` returns `status=failed`, `missing_knowledge_files` populated

### Test 3: Not a TileLang Repository
- **Input**: Random directory without TileLang indicators
- **Expected**: `inspect_tilelang_workspace` returns `status=failed`, `is_tilelang_repo=false`

## Knowledge Base Validation Tests

### Test 4: Valid Knowledge Base
- **Input**: Workspace with complete `tilelang_knowledge/`
- **Expected**: `validate_knowledge_base` returns `status=passed`, counts populated

### Test 5: Missing Files
- **Input**: `tilelang_knowledge/` missing `patterns.jsonl`
- **Expected**: `validate_knowledge_base` returns `status=failed`, `missing_files` includes `tilelang_knowledge/patterns.jsonl`

### Test 6: Parse Error
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

### Test 11: Pattern Search with Category Filter
- **Input**: `query="attention", category="attention_like_patterns"`
- **Expected**: Results filtered to attention patterns

### Test 12: API Lookup
- **Input**: `query="T.gemm"`
- **Expected**: Results include `T.gemm` with correct signature

## End-to-End Tests

### Test 13: Basic GEMM Workflow
1. Validate workspace
2. Validate knowledge base
3. Normalize device (H100)
4. Search capabilities for "GEMM"
5. Search patterns for "GEMM"
6. Lookup APIs for ["T.gemm"]
7. Build retrieval plan

**Expected**: All steps succeed, final plan has `status=passed`

### Test 14: Failure Recovery
1. Validate workspace (fails - not TileLang repo)
2. Stop and report error

**Expected**: Skill stops immediately, does not attempt code generation
