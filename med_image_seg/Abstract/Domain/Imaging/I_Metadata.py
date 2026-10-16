from __future__ import annotations

from abc import ABC, abstractmethod


# 按键读取影像元数据，并以 JSON 快照保留原始字段。
class I_Metadata(ABC):
    # 返回记录的 JSON 文本快照，不暴露可变字典。
    @abstractmethod
    def getJson(self) -> str: ...

    # 按键取得文本元数据，缺失时使用调用方提供的默认值。
    @abstractmethod
    def getText(self, key: str, default: str = "") -> str: ...

    # 按元数据键和元素索引读取数值字段。
    @abstractmethod
    def getNumber(self, key: str, index: int) -> float: ...
