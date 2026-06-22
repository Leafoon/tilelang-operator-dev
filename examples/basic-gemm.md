# Example: Basic GEMM Operator

This example shows how to use the skill to develop a basic GEMM operator.

## User Request

"Write a TileLang GEMM kernel for H100"

## Expected Workflow

1. **Workspace Validation**
   ```
   Call: inspect_tilelang_workspace
   Result: status=passed, is_tilelang_repo=true
   ```

2. **Knowledge Validation**
   ```
   Call: validate_knowledge_base
   Result: status=passed, counts={patterns.jsonl: 42, apis.jsonl: 156}
   ```

3. **Device Normalization**
   ```
   Call: normalize_device_profile(vendor="NVIDIA", model="H100")
   Result: vendor=NVIDIA, suggested_target="cuda -arch=sm_90", confidence=0.9
   ```

4. **Capability Search**
   ```
   Call: search_capabilities(query="GEMM matrix multiply")
   Result: capability_id="gemm_like_patterns"
   ```

5. **Pattern Search**
   ```
   Call: search_patterns(query="GEMM", capability_id="gemm_like_patterns")
   Result: pattern_id="basic_gemm_pattern"
   ```

6. **API Lookup**
   ```
   Call: lookup_apis(symbols=["T.gemm", "T.Kernel", "T.alloc_shared"])
   Result: API signatures and visibility
   ```

7. **Generate Code** (only after retrieval trace is complete)

## Output Format

```markdown
## Workspace Check
- TileLang repository: /path/to/tilelang
- Knowledge base: /path/to/tilelang/tilelang_knowledge
- Validation: passed

## Operator Intent
- Type: GEMM
- Target: NVIDIA H100 (sm_90)

## Retrieval Trace
- capability_id: gemm_like_patterns
- pattern_id: basic_gemm_pattern
- confidence: high

## Implementation
[Generated TileLang code here]

## Validation Plan
[Steps to verify the kernel]
```
