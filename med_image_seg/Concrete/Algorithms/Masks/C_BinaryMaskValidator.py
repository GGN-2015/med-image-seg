from __future__ import annotations

from typing import final

import numpy as np
from numpy.typing import NDArray

from ....Abstract.Algorithms.Masks.I_BinaryMaskValidator import I_BinaryMaskValidator


# 校验三维掩码数组，并把所有非零标签统一为前景。
@final
class C_BinaryMaskValidator(I_BinaryMaskValidator):
    # 拒绝空数组、非三维或非有限数据，将所有非零标签转换为二值前景。
    def validate(self, data: NDArray[np.generic]) -> NDArray[np.uint8]:
        from ...Numerics.Arrays.C_ArrayFactory import C_ArrayFactory

        if data.ndim != 3 or any(size == 0 for size in data.shape):
            raise ValueError("external mask must be a nonempty 3-D array")
        if data.dtype.kind not in "buif" or not np.isfinite(data).all():
            raise ValueError("external mask must contain finite real numeric values")
        return C_ArrayFactory().wrap(np.asarray(data != 0, dtype=np.uint8))
