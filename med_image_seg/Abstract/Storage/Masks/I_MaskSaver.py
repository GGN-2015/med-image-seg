from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..Paths.I_FilePath import I_FilePath
from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray


# 按指定几何保存掩码，供应用层在不接触文件格式库时调用。
class I_MaskSaver(ABC):
    # 按指定间距和原点保存掩码，格式与路径兼容交由掩码写入器处理。
    @abstractmethod
    def save_mask(
        self,
        path: str | I_FilePath,
        mask: NDArray[np.generic],
        *,
        spacing_mm: tuple[float, float, float],
        origin_lps_mm: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> I_FilePath: ...
