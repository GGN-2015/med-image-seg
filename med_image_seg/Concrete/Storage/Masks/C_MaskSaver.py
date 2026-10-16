from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Storage.Masks.I_MaskSaver import I_MaskSaver

if TYPE_CHECKING:
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
from typing import final

import numpy as np
from numpy.typing import NDArray


# 按指定几何保存掩码，供应用层在不接触文件格式库时调用。
@final
class C_MaskSaver(I_MaskSaver):
    # 按指定间距和原点保存掩码，格式与路径兼容交由掩码写入器处理。
    def save_mask(
        self,
        path: str | I_FilePath,
        mask: NDArray[np.generic],
        *,
        spacing_mm: tuple[float, float, float],
        origin_lps_mm: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> I_FilePath:
        from .C_MedicalMaskWriter import C_MedicalMaskWriter

        return C_MedicalMaskWriter().write_geometry(
            path, mask, spacing_mm=spacing_mm, origin_lps_mm=origin_lps_mm
        )
