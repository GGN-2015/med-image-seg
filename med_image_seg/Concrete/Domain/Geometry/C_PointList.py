from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import final

from ....Abstract.Domain.Geometry.I_Point2D import I_Point2D
from ....Abstract.Domain.Geometry.I_PointList import I_PointList


# 保存有序顶点快照，按索引提供只读坐标而不泄漏可变容器。
@final
@dataclass(frozen=True, slots=True, init=False)
class C_PointList(I_PointList):
    _points: tuple[I_Point2D, ...]

    # 逐项复制二维坐标，避免输入容器或点对象影响已保存顶点。
    def __init__(self, points: Iterable[tuple[float, float] | I_Point2D]) -> None:
        from ....Abstract.Domain.Geometry.I_Point2D import I_Point2D
        from .C_Point2D import C_Point2D

        object.__setattr__(
            self,
            "_points",
            tuple(
                C_Point2D(point.getX(), point.getY())
                if isinstance(point, I_Point2D)
                else C_Point2D(*point)
                for point in points
            ),
        )

    # 返回轮廓顶点数量。
    def getCount(self) -> int:
        return len(self._points)

    # 按索引读取只读二维顶点，保持输入顺序和数值精度。
    def getPoint(self, index: int) -> I_Point2D:
        return self._points[index]
