from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Domain.Annotations.I_PolygonAnnotation import I_PolygonAnnotation
from ....Abstract.Domain.Geometry.I_PointList import I_PointList
from ....Abstract.Domain.Snapshots.I_PolygonCopy import I_PolygonCopy

if TYPE_CHECKING:
    from ....Abstract.Domain.Annotations.I_PolygonAnnotation import I_PolygonAnnotation
from typing import final


# 复制轮廓并替换指定字段，保留未修改的坐标、来源和编辑顺序。
@final
class C_PolygonCopy(I_PolygonCopy):
    # 复制多边形并替换指定字段，未指定的字段沿用原值。
    def copy(
        self,
        polygon: I_PolygonAnnotation,
        *,
        edit_order: int,
        points: I_PointList | None = None,
        source: str | None = None,
    ) -> I_PolygonAnnotation:
        from ..Annotations.C_PolygonAnnotation import C_PolygonAnnotation

        return C_PolygonAnnotation(
            points=polygon.getPoints() if points is None else points,
            operation=polygon.getOperation(),
            source=polygon.getSource() if source is None else source,
            edit_order=edit_order,
        )
