from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Domain.Annotations.I_PolygonAnnotation import I_PolygonAnnotation
from abc import ABC, abstractmethod


# 检查多边形操作、来源和顶点有效性，阻止无效轮廓进入项目。
class I_PolygonValidator(ABC):
    # 检查添加或擦除类型、轮廓来源、至少三个顶点及坐标有限性。
    @abstractmethod
    def validate(self, context: I_PolygonAnnotation) -> None: ...
