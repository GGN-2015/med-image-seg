from __future__ import annotations

from typing import final

from ....Abstract.Algorithms.Observation.I_OverlayPalette import I_OverlayPalette


# 提供外置掩码的半透明淡红色，避免各视图自行选择配色。
@final
class C_OverlayPalette(I_OverlayPalette):
    # 返回外置掩码使用的半透明淡红色。
    def getExternalMaskColor(self) -> tuple[int, int, int, int]:
        return (255, 128, 128, 90)
