from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ....Abstract.Domain.Geometry.I_Point2D import I_Point2D


# 表示只读二维坐标，供轮廓算法在不依赖 Qt 的情况下读取顶点。
@final
@dataclass(frozen=True, slots=True)
class C_Point2D(I_Point2D):
    _x: float
    _y: float

    # 返回二维顶点的横坐标。
    def getX(self) -> float:
        return self._x

    # 返回二维顶点的纵坐标。
    def getY(self) -> float:
        return self._y
