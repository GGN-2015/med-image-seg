from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import final

from ....Abstract.Domain.Records.I_RecordFieldList import I_RecordFieldList


# 按顺序提供记录字段名，用只读查询替代可变字段列表。
@final
@dataclass(frozen=True, slots=True, init=False)
class C_RecordFieldList(I_RecordFieldList):
    _fields: tuple[str, ...]

    # 复制字段名称为有序只读快照。
    def __init__(self, fields: Iterable[str]) -> None:
        object.__setattr__(self, "_fields", tuple(fields))

    # 返回记录字段数量。
    def getCount(self) -> int:
        return len(self._fields)

    # 按索引查询记录字段名，保持既定序列化顺序。
    def getField(self, index: int) -> str:
        return self._fields[index]
