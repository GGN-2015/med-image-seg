from __future__ import annotations

from abc import abstractmethod

from ..Geometry.I_PointList import I_PointList
from ..Records.I_RecordFieldList import I_RecordFieldList
from .I_Record import I_Record


# 保存不可变轮廓及编辑顺序，使用只读顶点集合避免外部篡改。
class I_PolygonAnnotation(I_Record):
    # 通过只读顶点集合访问轮廓坐标，不泄漏嵌套列表。
    @abstractmethod
    def getPoints(self) -> I_PointList: ...

    # 返回添加或擦除区域的操作类型。
    @abstractmethod
    def getOperation(self) -> str: ...

    # 返回 manual 或 prototype 来源，复核不会改变原来源。
    @abstractmethod
    def getSource(self) -> str: ...

    # 返回轮廓最近一次编辑的顺序号。
    @abstractmethod
    def getEditOrder(self) -> int: ...

    # 返回有序的记录字段名，供序列化读取。
    @abstractmethod
    def getRecordFields(self) -> I_RecordFieldList: ...
