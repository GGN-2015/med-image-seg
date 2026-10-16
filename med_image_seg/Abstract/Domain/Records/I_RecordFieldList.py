from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import final


# 按顺序提供记录字段名，用只读查询替代可变字段列表。
class I_RecordFieldList(ABC):
    # 返回记录字段数量。
    @abstractmethod
    def getCount(self) -> int: ...

    # 按索引查询记录字段名，保持既定序列化顺序。
    @abstractmethod
    def getField(self, index: int) -> str: ...

    # 返回集合项数，支持 Python 长度协议。
    @final
    def __len__(self) -> int:
        return self.getCount()

    # 按索引查询单项，不向调用方返回内部集合。
    @final
    def __getitem__(self, index: int) -> str:
        return self.getField(index)

    # 依次查询集合元素，保留原有顺序且不暴露存储容器。
    @final
    def __iter__(self) -> Iterator[str]:
        for index in range(self.getCount()):
            yield self.getField(index)
