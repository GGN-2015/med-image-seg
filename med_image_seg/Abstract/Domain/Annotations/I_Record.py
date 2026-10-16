from __future__ import annotations

from abc import ABC, abstractmethod

from ..Records.I_RecordFieldList import I_RecordFieldList


# 提供持久化字段的只读查询，让记录对象与序列化方式解耦。
class I_Record(ABC):
    # 返回有序的记录字段名，供序列化读取。
    @abstractmethod
    def getRecordFields(self) -> I_RecordFieldList: ...
