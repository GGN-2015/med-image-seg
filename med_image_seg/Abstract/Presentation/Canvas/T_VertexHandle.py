from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TypeVar

from ..Window.T_HostedObject import T_HostedObject

T_Host = TypeVar("T_Host", covariant=True)


# 表示可拖动顶点，携带多边形和顶点索引以定位编辑目标。
class T_VertexHandle(T_HostedObject[T_Host], Generic[T_Host]):
    # 返回顶点控件所属的多边形索引。
    @abstractmethod
    def getPolygonIndex(self) -> int: ...

    # 返回顶点在所属轮廓中的索引。
    @abstractmethod
    def getVertexIndex(self) -> int: ...
