from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import final

from ....Abstract.Domain.Annotations.I_PolygonAnnotation import I_PolygonAnnotation
from ....Abstract.Domain.Geometry.I_Point2D import I_Point2D
from ....Abstract.Domain.Geometry.I_PointList import I_PointList
from ....Abstract.Domain.Records.I_RecordFieldList import I_RecordFieldList


# 保存不可变轮廓及编辑顺序，使用只读顶点集合避免外部篡改。
@final
@dataclass(slots=True, frozen=True, init=False)
class C_PolygonAnnotation(I_PolygonAnnotation):
    _state_points: I_PointList
    _state_operation: str
    _state_source: str
    _state_edit_order: int

    # 复制顶点形成只读快照，并校验操作、来源和顶点有效性。
    def __init__(
        self,
        points: I_PointList | Iterable[I_Point2D | tuple[float, float]],
        operation: str = "add",
        source: str = "manual",
        edit_order: int = 0,
    ) -> None:
        from ..Geometry.C_PointList import C_PointList

        object.__setattr__(self, "_state_points", C_PointList(points))
        object.__setattr__(self, "_state_operation", operation)
        object.__setattr__(self, "_state_source", source)
        object.__setattr__(self, "_state_edit_order", edit_order)
        self.__post_init__()

    # 通过只读顶点集合访问轮廓坐标，不泄漏嵌套列表。
    def getPoints(self) -> I_PointList:
        return self._state_points

    # 返回添加或擦除区域的操作类型。
    def getOperation(self) -> str:
        return self._state_operation

    # 返回 manual 或 prototype 来源，复核不会改变原来源。
    def getSource(self) -> str:
        return self._state_source

    # 返回轮廓最近一次编辑的顺序号。
    def getEditOrder(self) -> int:
        return self._state_edit_order

    # 返回有序的记录字段名，供序列化读取。
    def getRecordFields(self) -> I_RecordFieldList:
        from ..Records.C_RecordFieldList import C_RecordFieldList

        return C_RecordFieldList(("points", "operation", "source", "edit_order"))

    # 委托轮廓校验器检查操作、来源和顶点，构造时即拒绝无效多边形。
    def __post_init__(self) -> None:
        from ...Algorithms.Validation.C_PolygonValidator import C_PolygonValidator

        return C_PolygonValidator().validate(self)
