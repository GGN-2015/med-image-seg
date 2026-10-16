from __future__ import annotations

from typing import TYPE_CHECKING

from ..Annotations.I_PolygonAnnotation import I_PolygonAnnotation
from ..Geometry.I_PointList import I_PointList

if TYPE_CHECKING:
    from ..Annotations.I_PolygonAnnotation import I_PolygonAnnotation
from abc import ABC, abstractmethod


# 复制轮廓并替换指定字段，保留未修改的坐标、来源和编辑顺序。
class I_PolygonCopy(ABC):
    # 复制多边形并替换指定字段，未指定的字段沿用原值。
    @abstractmethod
    def copy(
        self,
        polygon: I_PolygonAnnotation,
        *,
        edit_order: int,
        points: I_PointList | None = None,
        source: str | None = None,
    ) -> I_PolygonAnnotation: ...
