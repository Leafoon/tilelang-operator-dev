# Example Matrix Multiply Operator

This is a minimal TileLang operator template that mirrors the style of the
official GEMM examples.

## Overview

This operator implements a basic tiled matrix multiplication using `T.gemm`.
Use it as a starting point, then retrieve the closest pattern and API evidence
from `tilelang-operator-knowledge` before adding target-specific features.

## Usage

```python
import torch
from operator import example_matrix_multiply

M, N, K = 512, 512, 512
A = torch.randn(M, K, device="cuda")
B = torch.randn(K, N, device="cuda")
C = torch.empty(M, N, device="cuda", dtype=torch.float16)

kernel = example_matrix_multiply(M, N, K)
kernel(A, B, C)
```

## Performance

| Size          | Average Time (ms) | TFLOPS |
|---------------|-------------------|--------|
| 256x256x256   |                   |        |
| 512x512x512   |                   |        |
| 1024x1024x1024|                   |        |

## Implementation Details

- Tile size: 128x128x32
- Pipeline stages: 3
- Threads per block: 128
- Uses shared memory for tile staging
- Uses `T.gemm`; exact lowering depends on target, dtype, and TileLang passes

## Test Results

Run the tests:
```bash
python -m pytest test_operator.py -v
```

## Benchmark Results

Run the benchmarks:
```bash
python benchmark.py
```

## Optimization Opportunities

- [ ] Retrieve target-specific GEMM, WGMMA, TCGEN05, or MFMA evidence before changing the intrinsic path
- [ ] Optimize pipeline stages and prefetching
- [ ] Add support for mixed precision (FP8/BF16)
- [ ] Implement split-K for larger K dimensions
- [ ] Add autotuning configuration

## Known Limitations

- Example tests assume a CUDA runtime and tile-aligned sizes
- Fixed tile size configuration
- No boundary masking or dynamic shape support yet

## References

- Official TileLang `examples/gemm/example_gemm.py`
- TileLang Operator Skill retrieval results for the selected device
