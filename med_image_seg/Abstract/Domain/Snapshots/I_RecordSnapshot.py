from __future__ import annotations

from abc import ABC, abstractmethod


# 封装序列化后的 JSON 文本，避免向调用方暴露可变字典。
class I_RecordSnapshot(ABC):
    # 返回记录的 JSON 文本快照，不暴露可变字典。
    @abstractmethod
    def getJson(self) -> str: ...
