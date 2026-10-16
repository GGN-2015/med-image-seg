from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Algorithms.Validation.I_PolygonValidator import I_PolygonValidator
from ....Abstract.Domain.Annotations.I_PolygonAnnotation import I_PolygonAnnotation

if TYPE_CHECKING:
    from ....Abstract.Domain.Annotations.I_PolygonAnnotation import I_PolygonAnnotation
from typing import final

import numpy as np


# 检查多边形操作、来源和顶点有效性，阻止无效轮廓进入项目。
@final
class C_PolygonValidator(I_PolygonValidator):
    # 检查添加或擦除类型、轮廓来源、至少三个顶点及坐标有限性。
    def validate(self, context: I_PolygonAnnotation) -> None:
        if context.getOperation() not in ("add", "erase"):
            raise ValueError("operation must be 'add' or 'erase'")
        if context.getSource() not in ("manual", "prototype"):
            raise ValueError("source must be 'manual' or 'prototype'")
        if len(context.getPoints()) < 3:
            raise ValueError("a polygon needs at least three points")
        if not all(
            np.isfinite((point.getX(), point.getY())).all()
            for point in context.getPoints()
        ):
            raise ValueError("polygon points must be finite")
        if context.getEditOrder() < 0:
            raise ValueError("edit_order must not be negative")
