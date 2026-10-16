from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import final

from ..Imaging.I_ImageSource import I_ImageSource


# 按指纹去重并保留导入顺序，通过数量、索引和指纹查询影像。
class I_ImageCollection(ABC):
    # 返回按指纹去重后的影像数量。
    @abstractmethod
    def getCount(self) -> int: ...

    # 按导入顺序查询指定索引的影像源，不暴露内部列表。
    @abstractmethod
    def getSource(self, index: int) -> I_ImageSource: ...

    # 按指纹查询已导入影像，不存在时返回空值。
    @abstractmethod
    def findByFingerprint(self, fingerprint: str) -> I_ImageSource | None: ...

    # 返回集合项数，支持 Python 长度协议。
    @final
    def __len__(self) -> int:
        return self.getCount()

    # 依次查询集合元素，保留原有顺序且不暴露存储容器。
    @final
    def __iter__(self) -> Iterator[I_ImageSource]:
        for index in range(self.getCount()):
            yield self.getSource(index)

    # 按索引查询单项，不向调用方返回内部集合。
    @final
    def __getitem__(self, index: int) -> I_ImageSource:
        return self.getSource(index)
