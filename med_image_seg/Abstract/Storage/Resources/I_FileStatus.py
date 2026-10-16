from __future__ import annotations

from abc import ABC, abstractmethod


# 提供文件大小和修改时间，供影像指纹计算而不依赖原生 stat 结构。
class I_FileStatus(ABC):
    # 返回文件大小，单位为字节。
    @abstractmethod
    def getSize(self) -> int: ...

    # 返回文件修改时间的纳秒值。
    @abstractmethod
    def getModifiedNs(self) -> int: ...
