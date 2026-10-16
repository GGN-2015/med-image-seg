from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import final

from .I_Point2D import I_Point2D


# 保存有序顶点快照，按索引提供只读坐标而不泄漏可变容器。
class I_PointList(ABC):
    # 返回轮廓顶点数量。
    @abstractmethod
    def getCount(self) -> int: ...

    # 按索引读取只读二维顶点，保持输入顺序和数值精度。
    @abstractmethod
    def getPoint(self, index: int) -> I_Point2D: ...

    # 返回集合项数，支持 Python 长度协议。
    @final
    def __len__(self) -> int:
        return self.getCount()

    # 按索引查询单项，不向调用方返回内部集合。
    @final
    def __getitem__(self, index: int) -> I_Point2D:
        return self.getPoint(index)

    # 依次查询集合元素，保留原有顺序且不暴露存储容器。
    @final
    def __iter__(self) -> Iterator[I_Point2D]:
        for index in range(self.getCount()):
            yield self.getPoint(index)
