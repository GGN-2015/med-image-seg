from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ....Abstract.Storage.Resources.I_FileStatus import I_FileStatus


# 提供文件大小和修改时间，供影像指纹计算而不依赖原生 stat 结构。
@final
@dataclass(frozen=True)
class C_FileStatus(I_FileStatus):
    _size: int
    _modified_ns: int

    # 返回文件大小，单位为字节。
    def getSize(self) -> int:
        return self._size

    # 返回文件修改时间的纳秒值。
    def getModifiedNs(self) -> int:
        return self._modified_ns
