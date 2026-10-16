from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from .I_SliceAnnotation import I_SliceAnnotation

if TYPE_CHECKING:
    from .I_PolygonAnnotation import I_PolygonAnnotation
from abc import abstractmethod


# 在只读层标注上增加轮廓和复核标志的受控修改，不开放内部列表。
class I_MutableSliceAnnotation(I_SliceAnnotation):
    # 用输入轮廓替换本层内容，复制集合以隔离调用方的后续修改。
    @abstractmethod
    def setPolygons(self, value: Iterable[I_PolygonAnnotation]) -> None: ...

    # 记录当前层是否已完成复核。
    @abstractmethod
    def setCompleted(self, value: bool) -> None: ...

    # 记录当前层是否作为显式插值关键层。
    @abstractmethod
    def setKeyframe(self, value: bool) -> None: ...

    # 记录当前层是否强制无掩码。
    @abstractmethod
    def setForceEmpty(self, value: bool) -> None: ...

    # 在当前层末尾追加轮廓，不暴露内部多边形列表。
    @abstractmethod
    def addPolygon(self, polygon: I_PolygonAnnotation) -> None: ...

    # 按索引替换已有轮廓，不允许调用方直接修改存储列表。
    @abstractmethod
    def replacePolygon(self, index: int, polygon: I_PolygonAnnotation) -> None: ...

    # 按索引移除轮廓并返回被移除项，集合本身仍由切片对象管理。
    @abstractmethod
    def removePolygon(self, index: int) -> I_PolygonAnnotation: ...
