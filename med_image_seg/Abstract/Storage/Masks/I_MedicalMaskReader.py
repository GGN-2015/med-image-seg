from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from ..Paths.I_FilePath import I_FilePath
from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray


# 读取 NIfTI 或 UBD 掩码，并按物理坐标对齐到参考影像网格。
class I_MedicalMaskReader(ABC):
    # 读取 NIfTI 或 UBD 掩码，以最近邻对齐参考网格并检查物理覆盖范围。
    @abstractmethod
    def read(
        self, path: str | I_FilePath, reference: I_MedicalVolume
    ) -> NDArray[np.uint8]: ...
