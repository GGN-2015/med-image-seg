from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ....Abstract.Domain.Snapshots.I_RecordSnapshot import I_RecordSnapshot


# 封装序列化后的 JSON 文本，避免向调用方暴露可变字典。
@final
@dataclass(frozen=True)
class C_RecordSnapshot(I_RecordSnapshot):
    _json: str

    # 返回记录的 JSON 文本快照，不暴露可变字典。
    def getJson(self) -> str:
        return self._json
