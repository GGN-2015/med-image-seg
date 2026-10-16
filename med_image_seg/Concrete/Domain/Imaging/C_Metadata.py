from __future__ import annotations

import json
from dataclasses import dataclass
from typing import final

from ....Abstract.Domain.Imaging.I_Metadata import I_Metadata


# 按键读取影像元数据，并以 JSON 快照保留原始字段。
@final
@dataclass(frozen=True)
class C_Metadata(I_Metadata):
    _json: str = "{}"

    # 返回记录的 JSON 文本快照，不暴露可变字典。
    def getJson(self) -> str:
        return self._json

    # 按键取得文本元数据，缺失时使用调用方提供的默认值。
    def getText(self, key: str, default: str = "") -> str:
        return str(json.loads(self._json).get(key, default))

    # 按元数据键和元素索引读取数值字段。
    def getNumber(self, key: str, index: int) -> float:
        return float(json.loads(self._json)[key][index])
