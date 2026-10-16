from __future__ import annotations

from typing import final

import numpy as np

from ....Abstract.Algorithms.Validation.I_SpacingValidator import I_SpacingValidator


# 检查标注网格间距为有限正数，统一读取器的输入要求。
@final
class C_SpacingValidator(I_SpacingValidator):
    # 拒绝非有限或非正的网格间距，返回规范的浮点值。
    def validate(self, spacing_mm: float) -> float:
        if not np.isfinite(spacing_mm) or spacing_mm <= 0:
            raise ValueError("spacing_mm must be a finite number greater than zero")
        return float(spacing_mm)
