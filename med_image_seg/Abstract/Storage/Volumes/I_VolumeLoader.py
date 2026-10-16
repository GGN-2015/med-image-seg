from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from ...Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from ..Paths.I_FilePath import I_FilePath
from abc import ABC, abstractmethod


# 按指定间距加载医学影像，将读取器的构造细节留在存储层。
class I_VolumeLoader(ABC):
    # 按指定间距读取并重采样医学影像，返回体积接口。
    @abstractmethod
    def load_volume(
        self,
        path: str | I_FilePath,
        spacing_mm: float = 0.8,
        *,
        interpolation: Literal["linear", "nearest"] = "linear",
    ) -> I_MedicalVolume: ...
