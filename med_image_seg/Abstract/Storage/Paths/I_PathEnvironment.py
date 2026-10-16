from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .I_FilePath import I_FilePath
from abc import ABC, abstractmethod


# 提供工作目录，供临时路径回退策略查询运行环境。
class I_PathEnvironment(ABC):
    # 返回进程当前工作目录。
    @abstractmethod
    def getWorkingDirectory(self) -> I_FilePath: ...
