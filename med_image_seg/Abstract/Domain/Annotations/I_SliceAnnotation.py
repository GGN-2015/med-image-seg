from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from ..Records.I_RecordFieldList import I_RecordFieldList
from .I_PolygonAnnotation import I_PolygonAnnotation
from .I_Record import I_Record

if TYPE_CHECKING:
    from .I_PolygonAnnotation import I_PolygonAnnotation
from abc import abstractmethod
from typing import final


# 管理单层轮廓与复核标志，按索引访问多边形而不暴露内部列表。
class I_SliceAnnotation(I_Record):
    # 返回当前层是否已复核。
    @abstractmethod
    def getCompleted(self) -> bool: ...

    # 返回当前层是否被显式设为插值关键层。
    @abstractmethod
    def getKeyframe(self) -> bool: ...

    # 返回本层是否强制无掩码；该状态优先于轮廓与插值。
    @abstractmethod
    def getForceEmpty(self) -> bool: ...

    # 返回有序的记录字段名，供序列化读取。
    @abstractmethod
    def getRecordFields(self) -> I_RecordFieldList: ...

    # 返回本层已存轮廓数量，包括被强制空层屏蔽的轮廓。
    @abstractmethod
    def getPolygonCount(self) -> int: ...

    # 按索引查询本层轮廓，不允许调用方直接修改集合结构。
    @abstractmethod
    def getPolygon(self, index: int) -> I_PolygonAnnotation: ...

    # 按存储顺序迭代本层轮廓，不向调用方暴露列表。
    @final
    def iterPolygons(self) -> Iterator[I_PolygonAnnotation]:
        for index in range(self.getPolygonCount()):
            yield self.getPolygon(index)
