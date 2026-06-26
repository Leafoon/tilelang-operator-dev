"""Test suite for example operator.

Replace with tests for your actual operator.
"""
import pytest
import torch

# Import your operator
from .operator import example_matrix_multiply


def test_correctness():
    """Test operator correctness against reference implementation."""
    M, N, K = 256, 256, 256

    # Create test inputs
    A = torch.randn(M, K, device="cuda")
    B = torch.randn(K, N, device="cuda")

    # Reference implementation
    C_ref = A @ B

    # TileLang operator
    kernel = example_matrix_multiply(M, N, K)
    C_tl = torch.empty_like(C_ref)
    kernel(A, B, C_tl)

    # Validate
    torch.testing.assert_close(C_tl, C_ref, rtol=1e-3, atol=1e-3)
    print("Correctness test passed!")


def test_different_sizes():
    """Test operator with various input sizes."""
    sizes = [(128, 128, 128), (256, 128, 256), (512, 512, 64)]

    for M, N, K in sizes:
        A = torch.randn(M, K, device="cuda")
        B = torch.randn(K, N, device="cuda")
        C_ref = A @ B

        kernel = example_matrix_multiply(M, N, K)
        C_tl = torch.empty_like(C_ref)
        kernel(A, B, C_tl)

        torch.testing.assert_close(C_tl, C_ref, rtol=1e-3, atol=1e-3)
        print(f"Size ({M}, {N}, {K}) passed!")


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    # Small sizes
    M, N, K = 32, 32, 32
    A = torch.randn(M, K, device="cuda")
    B = torch.randn(K, N, device="cuda")
    C_ref = A @ B

    kernel = example_matrix_multiply(M, N, K)
    C_tl = torch.empty_like(C_ref)
    kernel(A, B, C_tl)

    torch.testing.assert_close(C_tl, C_ref, rtol=1e-3, atol=1e-3)
    print("Edge case test passed!")


if __name__ == "__main__":
    test_correctness()
    test_different_sizes()
    test_edge_cases()
    print("All tests passed!")
