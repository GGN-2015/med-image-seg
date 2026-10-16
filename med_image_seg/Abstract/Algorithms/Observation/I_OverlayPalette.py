from __future__ import annotations

from abc import ABC, abstractmethod


# 提供外置掩码的半透明淡红色，避免各视图自行选择配色。
class I_OverlayPalette(ABC):
    # 返回外置掩码使用的半透明淡红色。
    @abstractmethod
    def getExternalMaskColor(self) -> tuple[int, int, int, int]: ...
