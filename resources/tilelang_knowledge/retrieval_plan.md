# Retrieval Plan For TileLang Operator Development

Use this plan when a user asks for a new TileLang operator such as GEMM variants, attention kernels, reductions, fused elementwise ops, or convolution-like kernels. If the user provides a target vendor/model, resolve that device profile before selecting patterns or intrinsics.

## Step 0: Resolve Device Profile

When the request includes a hardware vendor/model, normalize it into:

- `vendor`: NVIDIA, AMD, CPU, Apple, WebGPU, or other.
- `model`: for example A100, H100, B100, MI300X, MI350, M2, EPYC.
- `target`: for example `cuda -arch=sm_80`, `cuda -arch=sm_90`, `cuda -arch=sm_100a`, `hip -mcpu=gfx950`, `llvm`, `c`, `metal`, or `webgpu`.

Use `capability_map.json.device_integration_schema` as the schema. If only vendor is known, use the documented base target but avoid architecture-specific intrinsics until the model/arch is confirmed.

## Step 1: Classify The Request

Open `capability_map.json` first. Identify one or more capability IDs and inspect each entry's `device_adaptation`:

- `gemm_like_patterns` for dense, split-K, grouped/MoE, sparse, FP8/int4, dequantized, dynamic-shape, or epilogue-fused matmul.
- `attention_like_patterns` for MHA/GQA/MLA, flash attention, decode, paged KV, and online softmax attention.
- `reductions` for reductions, softmax, norms, cumsum, and top-k support.
- `memory_movement` when the hard part is staging, async copy, TMA, or shared/local/fragment movement.
- `tiling_and_schedule` or `pipelining` when block sizes, loop structure, layout, or software pipeline are central.
- `tensor_intrinsics` when using `T.gemm`, WGMMA, TCGEN05, MFMA, or sparse GEMM.
- `lowering_or_codegen_related_components` only for compile/lowering behavior and backend constraints.
- `testing_and_validation_support` for correctness, benchmark, generated source, and profiler flows.

## Step 2: Select A Reusable Pattern

Search `patterns.jsonl` by `category`, `task_family`, `required_symbols`, and `related_patterns` from the capability entry.
Then inspect the selected pattern's `device_strategy` before writing code.

Use this layer to answer:

- How should the kernel body be organized?
- What buffers should be allocated and in which scope?
- What is the loop/control-flow shape?
- How does data move through global/shared/fragment/local memory?
- Which examples are closest to the target operator?

## Step 3: Recover The Usage Sequence

Search `usage_patterns.jsonl` by `usage_id`, `scenario`, and `symbols_used`.
Then inspect `device_execution_notes` for target-specific compile, tensor placement, profiler, and synchronization requirements.

Use this layer to answer:

- Should the implementation use lazy or eager `@tilelang.jit`?
- How is the kernel instantiated, compiled, called, validated, and benchmarked?
- What prerequisites and failure modes matter before writing code?
- What is the smallest practical call flow to reuse?

## Step 4: Confirm APIs And Boundaries

Search `apis.jsonl` by exact symbol names from the selected pattern and usage records.

Use this layer to answer:

- What is the signature?
- Is the symbol public/exported/internal/test-only?
- Which module should import it?
- Where is the source line range?
- What constraints appear in docstrings or summaries?

Avoid using internal symbols directly unless the record's evidence and source chunks justify it.

## Step 5: Fall Back To Source Chunks

Search `source_chunks.jsonl` when:

- A signature/docstring is not enough.
- The pattern is close but not specific enough.
- Shape/layout/memory-scope constraints are uncertain.
- A compiler error points to lowering, layout inference, copy, GEMM, or reduction behavior.
- Hardware-specific behavior such as WGMMA, TCGEN05, TMA, sparse GEMM, or async copy matters.

Prefer chunks whose `related_capabilities`, `related_patterns`, and `device_notes.applies_to` match the current task. Inspect `source` and then, only if still needed, open the original `file_path` around `start_line` and `end_line`.

## Step 6: Use The Semantic Graph For Dependency Tracing

Use `semantic_graph.json` when you need machine-readable relationships such as:

- capability -> pattern
- pattern -> required symbol
- module -> exposed symbol
- symbol -> lowering/transform path
- capability -> device family

Use `semantic_graph.mmd` for a quick human overview before diving into JSON.

## Step 7: Generate Or Modify The Operator

After retrieval, build the operator using the selected pattern and confirmed APIs. Include validation and benchmark steps from `usage_patterns.jsonl`. If new behavior relies on an inferred or low-confidence record, mention the uncertainty and verify against source chunks or tests.
