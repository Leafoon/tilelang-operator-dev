# Example Matrix Multiply Operator

This is an example operator to demonstrate the structure of a TileLang operator.

## Overview

This operator implements a basic tiled matrix multiplication using TileLang's GEMM intrinsic.

## Usage

```python
import torch
from operator import example_matrix_multiply

M, N, K = 512, 512, 512
A = torch.randn(M, K, device="cuda")
B = torch.randn(K, N, device="cuda")
C = torch.empty(M, N, device="cuda")

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
- Uses T.gemm intrinsic for tensor core acceleration

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

- [ ] Use WMMA intrinsics for better tensor core utilization
- [ ] Optimize pipeline stages and prefetching
- [ ] Add support for mixed precision (FP8/BF16)
- [ ] Implement split-K for larger K dimensions
- [ ] Add autotuning configuration

## Known Limitations

- Only works on NVIDIA GPUs with CUDA capability >= 7.0
- Fixed tile size configuration
- No dynamic shape support yet

## References

- TileLang GEMM documentation
- NVIDIA CUDA Programming Guide
- Tensor Core Performance Guide
