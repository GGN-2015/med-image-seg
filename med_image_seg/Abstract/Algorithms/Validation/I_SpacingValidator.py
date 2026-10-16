from __future__ import annotations

from abc import ABC, abstractmethod


# 检查标注网格间距为有限正数，统一读取器的输入要求。
class I_SpacingValidator(ABC):
    # 拒绝非有限或非正的网格间距，返回规范的浮点值。
    @abstractmethod
    def validate(self, spacing_mm: float) -> float: ...
