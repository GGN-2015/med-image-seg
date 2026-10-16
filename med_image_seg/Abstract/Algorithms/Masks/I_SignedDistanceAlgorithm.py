from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray


# 把二值切片转换为有符号距离场，供关键层之间的插值使用。
class I_SignedDistanceAlgorithm(ABC):
    # 计算二值切片的有符号距离场，为关键层之间的插值提供数值。
    @abstractmethod
    def signed_distance(self, plane: NDArray[np.bool_]) -> NDArray[np.float32]: ...
