"""Test suite for the example operator template."""
import torch

from .operator import example_matrix_multiply


def _run_case(M: int, N: int, K: int) -> None:
    A = torch.randn(M, K, device="cuda", dtype=torch.float16)
    B = torch.randn(K, N, device="cuda", dtype=torch.float16)
    C_ref = A @ B

    kernel = example_matrix_multiply(M, N, K)
    C_tl = torch.empty_like(C_ref)
    kernel(A, B, C_tl)

    torch.testing.assert_close(C_tl, C_ref, rtol=1e-2, atol=1e-2)


def test_correctness():
    """Test operator correctness against a PyTorch reference."""
    _run_case(256, 256, 256)


def test_different_sizes():
    """Test representative tile-aligned sizes."""
    for M, N, K in [(128, 128, 128), (256, 128, 256), (512, 512, 64)]:
        _run_case(M, N, K)


if __name__ == "__main__":
    test_correctness()
    test_different_sizes()
