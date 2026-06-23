# Example: Device Adaptation

This example shows how the skill adapts to different hardware targets.

## User Request

"Adapt the GEMM kernel for AMD MI300X"

## Device Normalization

### NVIDIA H100
```
Call: normalize_device_profile(vendor="NVIDIA", model="H100")
Result: vendor=NVIDIA, suggested_target="cuda -arch=sm_90", confidence=0.9
```

### AMD MI300X
```
Call: normalize_device_profile(vendor="AMD", model="MI300X")
Result: vendor=AMD, suggested_target="hip", confidence=0.5
Notes: "Exact AMD gfx architecture is unknown; do not invent gfxXXX."
```

> To get a specific gfx target, pass the architecture explicitly:
> ```
> Call: normalize_device_profile(vendor="AMD", model="MI300X", target="hip -mcpu=gfx940")
> Result: vendor=AMD, suggested_target="hip -mcpu=gfx940", confidence=0.75
> ```

### CPU
```
Call: normalize_device_profile(vendor="Intel", model="Xeon")
Result: vendor=CPU, suggested_target="llvm", confidence=0.8
```

## Device-Specific Fields

The skill uses these fields from knowledge base records:

- `device_adaptation`: Hardware-specific adjustments
- `device_strategy`: Optimization strategy for the device
- `device_execution_notes`: Runtime considerations
- `device_notes`: Additional hardware notes

## Conservative Recommendations

The skill is conservative with:
- WGMMA (NVIDIA only, verify support)
- TCGEN05 (Hopper+ only)
- TMA (Hopper+ only)
- cp.async (Ampere+)
- MFMA (AMD only)
- LDS (AMD shared memory)
- TMEM (verify support)
- cluster_dims (Hopper+)
- is_cpu=True (CPU backend only)
