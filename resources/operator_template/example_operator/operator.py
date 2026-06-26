"""Example TileLang operator template.

Replace this with your actual operator implementation.
"""
import tilelang
import tilelang.language as T


@tilelang.jit
def example_matrix_multiply(M: int, N: int, K: int):
    """Example matrix multiplication operator.

    This is a template to demonstrate the structure of a TileLang operator.
    Replace with your actual operator implementation.

    Args:
        M: Number of rows in A and C
        N: Number of columns in B and C
        K: Number of columns in A and rows in B
    """
    @T.prim_func
    def main(
        A: T.Tensor[M, K, dtype=T.float32],
        B: T.Tensor[K, N, dtype=T.float32],
        C: T.Tensor[M, N, dtype=T.float32],
    ):
        # Tile configuration - adjust based on your device
        block_M = 128
        block_N = 128
        block_K = 32

        with T.Kernel(M // block_M, N // block_N, threads=128) as (bx, by):
            A_shared = T.alloc_shared((block_M, block_K), dtype=T.float32)
            B_shared = T.alloc_shared((block_K, block_N), dtype=T.float32)
            C_local = T.alloc_fragment((block_M, block_N), dtype=T.float32)

            T.clear(C_local)

            for k in T.Parallel(K // block_K):
                with T.Pipelined(num_stages=3):
                    T.copy(A[bx * block_M : (bx + 1) * block_M, k * block_K : (k + 1) * block_K], A_shared)
                    T.copy(B[k * block_K : (k + 1) * block_K, by * block_N : (by + 1) * block_N], B_shared)

                T.gemm(A_shared, B_shared, C_local)

            T.copy(C_local, C[bx * block_M : (bx + 1) * block_M, by * block_N : (by + 1) * block_N])

    return main
