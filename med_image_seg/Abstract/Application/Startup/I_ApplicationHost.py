from __future__ import annotations

from typing import TYPE_CHECKING

from ...Domain.Collections.I_ImageCollection import I_ImageCollection

if TYPE_CHECKING:
    pass
from abc import ABC, abstractmethod


# 运行图形界面及事件循环，将界面框架隔离在应用入口之外。
class I_ApplicationHost(ABC):
    # 创建 Qt 应用和主窗口，进入事件循环并返回退出码。
    @abstractmethod
    def run(
        self,
        *,
        sources: I_ImageCollection | None = None,
        spacing_mm: float = 0.8,
        language: str = "en",
    ) -> int: ...
