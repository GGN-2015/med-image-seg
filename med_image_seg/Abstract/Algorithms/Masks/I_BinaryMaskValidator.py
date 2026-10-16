from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray


# 校验三维掩码数组，并把所有非零标签统一为前景。
class I_BinaryMaskValidator(ABC):
    # 拒绝空数组、非三维或非有限数据，将所有非零标签转换为二值前景。
    @abstractmethod
    def validate(self, data: NDArray[np.generic]) -> NDArray[np.uint8]: ...
