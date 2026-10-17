from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray

from ...Domain.Geometry.I_PointList import I_PointList


# 约定轮廓到像素掩码的转换，避免标注合成算法绑定到第三方的线程行为。
class I_PolygonRasterizer(ABC):
    # 在指定网格内判定轮廓内部和边界像素，网格外的轮廓不能写入结果。
    @abstractmethod
    def rasterize(
        self, points: I_PointList, width: int, height: int
    ) -> NDArray[np.bool_]: ...
