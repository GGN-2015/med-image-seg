from __future__ import annotations

from abc import abstractmethod
from typing import TypeVar

from .T_VertexHandle import T_VertexHandle

T_Host = TypeVar("T_Host", covariant=True)


# 在顶点索引查询上增加所属轮廓及顶点位置的更新入口。
class T_MutableVertexHandle(T_VertexHandle[T_Host]):
    # 记录顶点控件所属的多边形索引。
    @abstractmethod
    def setPolygonIndex(self, value: int) -> None: ...

    # 记录顶点在所属多边形中的索引。
    @abstractmethod
    def setVertexIndex(self, value: int) -> None: ...
