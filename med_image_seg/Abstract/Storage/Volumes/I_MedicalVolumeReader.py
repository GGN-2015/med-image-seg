from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from ...Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from ..Paths.I_FilePath import I_FilePath
from abc import ABC, abstractmethod


# 适配医学影像读取库，把输入重采样到指定间距的 LPS 网格。
class I_MedicalVolumeReader(ABC):
    # 返回读取器使用的标注网格间距。
    @abstractmethod
    def getInternalSpacingMm(self) -> float: ...

    # 返回 LPS 网格间距，单位为毫米。
    @abstractmethod
    def getSpacingMm(self) -> float: ...

    # 通过影像读取库加载输入，并重采样为指定间距的 LPS 体素和几何信息。
    @abstractmethod
    def read(
        self,
        path: str | I_FilePath,
        *,
        spacing_mm: float | None = None,
        interpolation: Literal["linear", "nearest"] = "linear",
    ) -> I_MedicalVolume: ...
