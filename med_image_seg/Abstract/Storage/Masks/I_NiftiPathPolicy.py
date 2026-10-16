from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..Resources.I_TemporaryDirectory import I_TemporaryDirectory
from abc import ABC, abstractmethod


# 选择纯英文临时目录并修正序列化间距，规避 NIfTI 路径和精度问题。
class I_NiftiPathPolicy(ABC):
    # 将间距向下修正到可序列化的 float32，避免写盘舍入扩大体素范围。
    @abstractmethod
    def nifti_safe_spacing(
        self, spacing_mm: tuple[float, float, float]
    ) -> tuple[float, ...]: ...

    # 优先选择可写的纯英文临时目录，必要时回退并报告无可用目录。
    @abstractmethod
    def ascii_temporary_directory(self) -> I_TemporaryDirectory: ...
