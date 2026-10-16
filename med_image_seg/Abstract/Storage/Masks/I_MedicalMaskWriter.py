from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from ..Paths.I_FilePath import I_FilePath
from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray


# 写出 NIfTI 或 UBD 掩码，保留物理几何并通过英文临时路径兼容中文目录。
class I_MedicalMaskWriter(ABC):
    # 使用参考影像的间距和原点保存掩码，确保输出几何与原影像一致。
    @abstractmethod
    def write(
        self,
        path: str | I_FilePath,
        mask: NDArray[np.generic],
        reference: I_MedicalVolume,
    ) -> I_FilePath: ...

    # 根据扩展名写出掩码，NIfTI 先写英文临时路径再复制到目标目录。
    @abstractmethod
    def write_geometry(
        self,
        path: str | I_FilePath,
        mask: NDArray[np.generic],
        *,
        spacing_mm: tuple[float, float, float],
        origin_lps_mm: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> I_FilePath: ...
