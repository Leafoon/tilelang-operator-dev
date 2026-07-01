"""Performance benchmark for the example operator template."""
import importlib.util
import time
from pathlib import Path

import torch

try:
    from .operator import example_matrix_multiply
except ImportError:
    spec = importlib.util.spec_from_file_location(
        "example_operator_impl",
        Path(__file__).with_name("operator.py"),
    )
    if spec is None or spec.loader is None:
        raise
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    example_matrix_multiply = module.example_matrix_multiply


def benchmark_operator(M, N, K, iterations=100, warmup=10):
    """Benchmark the TileLang operator."""
    A = torch.randn(M, K, device="cuda", dtype=torch.float16)
    B = torch.randn(K, N, device="cuda", dtype=torch.float16)
    C = torch.empty(M, N, device="cuda", dtype=torch.float16)

    kernel = example_matrix_multiply(M, N, K)

    # Warmup
    for _ in range(warmup):
        kernel(A, B, C)
    torch.cuda.synchronize()

    # Benchmark
    start = time.perf_counter()
    for _ in range(iterations):
        kernel(A, B, C)
    torch.cuda.synchronize()
    elapsed = time.perf_counter() - start

    avg_time_ms = (elapsed / iterations) * 1000
    tflops = (2 * M * N * K) / (avg_time_ms * 1e-3) / 1e12

    return {
        "size": (M, N, K),
        "avg_time_ms": avg_time_ms,
        "tflops": tflops,
        "iterations": iterations,
    }


def benchmark_reference(M, N, K, iterations=100, warmup=10):
    """Benchmark the reference implementation (cuBLAS)."""
    A = torch.randn(M, K, device="cuda", dtype=torch.float16)
    B = torch.randn(K, N, device="cuda", dtype=torch.float16)

    # Warmup
    for _ in range(warmup):
        C = A @ B
    torch.cuda.synchronize()

    # Benchmark
    start = time.perf_counter()
    for _ in range(iterations):
        C = A @ B
    torch.cuda.synchronize()
    elapsed = time.perf_counter() - start

    avg_time_ms = (elapsed / iterations) * 1000
    tflops = (2 * M * N * K) / (avg_time_ms * 1e-3) / 1e12

    return {
        "size": (M, N, K),
        "avg_time_ms": avg_time_ms,
        "tflops": tflops,
        "iterations": iterations,
    }


def run_comparison():
    """Run benchmark comparison between TileLang and reference."""
    sizes = [
        (256, 256, 256),
        (512, 512, 512),
        (1024, 1024, 1024),
        (2048, 2048, 2048),
    ]

    print(f"{'Size':<25} {'TileLang (ms)':<15} {'cuBLAS (ms)':<15} {'Speedup':<10}")
    print("-" * 70)

    for M, N, K in sizes:
        tl_result = benchmark_operator(M, N, K)
        ref_result = benchmark_reference(M, N, K)

        speedup = ref_result["avg_time_ms"] / tl_result["avg_time_ms"]
        size_str = f"{M}x{N}x{K}"

        print(
            f"{size_str:<25} "
            f"{tl_result['avg_time_ms']:<15.3f} "
            f"{ref_result['avg_time_ms']:<15.3f} "
            f"{speedup:<10.2f}x"
        )


if __name__ == "__main__":
    run_comparison()
